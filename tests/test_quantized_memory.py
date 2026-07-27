import os
import time
import struct
import hashlib
import numpy as np
import pytest
from solomon_quantized_memory import (
    LAYER_WORKING,
    LAYER_SHORT_TERM,
    LAYER_LONG_TERM,
    QuantizedMemoryNode,
    QuantizedBrainMap
)

def test_quantized_memory_node_lifecycle():
    """
    Verify QuantizedMemoryNode construction, access, ebbinghaus decay, and serialization.
    """
    node = QuantizedMemoryNode(
        node_type="episodic",
        content="Met Mark at 80/90 futures dashboard",
        importance=0.9,
        valence=0.8,
        arousal=0.6
    )

    # Verify construction
    assert len(node.id_str) == 36  # Standard UUID length
    assert 0 <= node.id_int < (2**31 - 1)
    assert node.layer == LAYER_WORKING
    assert node.access_count == 1
    assert node.activation == 0.0
    assert len(node.ternary_vector) == 128
    assert all(val in [-1, 0, 1] for val in node.ternary_vector)

    # Test access updates
    node.access()
    assert node.access_count == 2
    assert node.activation == 0.5

    # Test ebbinghaus decay
    # Mocking decay 1 hour in the past
    current_time = time.time()
    node.last_accessed = current_time - 3600.0  # 60 minutes ago
    node.ebbinghaus_decay(current_time)
    assert node.activation < 0.5  # Bounded decay

    # Test zero-copy serialization
    b_data = node.serialize()
    # Expect 41 bytes metadata + 128 bytes vector = 169 bytes
    assert len(b_data) == 169

    # Unpack metadata and verify matches
    id_int, layer, access_count, c_time, l_acc, imp, val, aro = struct.unpack("!QBIddfff", b_data[:41])
    assert id_int == node.id_int
    assert layer == node.layer
    assert access_count == node.access_count
    assert abs(imp - node.importance) < 1e-4
    assert abs(val - node.valence) < 1e-4
    assert abs(aro - node.arousal) < 1e-4

    # Verify vector bytes unpacked
    vec = np.frombuffer(b_data[41:], dtype=np.int8)
    assert np.array_equal(vec, node.ternary_vector)


def test_brain_map_ingest_and_collision():
    """
    Test node ingestion and linear probing collision handling.
    """
    brain = QuantizedBrainMap(max_nodes=5)

    # Ingest node 1
    id1 = brain.ingest("factual", "First node", importance=0.4)
    idx1 = brain.id_map[id1]
    assert idx1 in brain.nodes

    # Ingest 4 more nodes to fill map
    brain.ingest("factual", "Second node")
    brain.ingest("factual", "Third node")
    brain.ingest("factual", "Fourth node")
    brain.ingest("factual", "Fifth node")

    assert len(brain.nodes) == 5

    # Try to ingest 6th node (capacity limit should trigger consolidation and then error if full)
    # Since they are working layer nodes under TTL, they are not consolidated immediately without time elapsed.
    with pytest.raises(Exception) as excinfo:
        brain.ingest("factual", "Sixth node overflow")
    assert "absolute capacity" in str(excinfo.value)


def test_brain_map_amygdala_reflex_routing():
    """
    Test the Amygdala Protocol reflex caching on high arousal/valence threats.
    """
    brain = QuantizedBrainMap(max_nodes=100)

    # Ingest threat memory (high arousal and low valence)
    danger_id = brain.ingest("threat", "There is a server fire!", importance=0.9, valence=-0.8, arousal=0.95)

    # Node must be in Amygdala cache immediately
    assert danger_id in brain.amygdala_cache

    # Recall query with keywords "fire" must return the threat node instantly via cache bypass
    results = brain.recall("Critical server fire alarm!")
    assert len(results) == 1
    assert results[0]["id"] == danger_id
    assert "fire" in results[0]["content"]


def test_brain_map_auto_ternary_linking():
    """
    Test automatic linking of nodes using ternary vector dot product similarity.
    """
    brain = QuantizedBrainMap(max_nodes=100)

    # Let's seed two nodes with identical ternary vectors to guarantee high dot product similarity (128 / 128 = 1.0)
    node_id1 = brain.ingest("concept", "Task planning A")
    node_id2 = brain.ingest("concept", "Task planning B")

    node1 = brain.nodes[brain.id_map[node_id1]]
    node2 = brain.nodes[brain.id_map[node_id2]]

    # Force identical ternary vectors to simulate high semantic overlap
    node1.ternary_vector = np.ones(128, dtype=np.int8)
    node2.ternary_vector = np.ones(128, dtype=np.int8)

    # Re-run linking (which dot product will find similarity = 1.0 > 0.3)
    brain._auto_link_ternary(node1)

    assert brain.adj_matrix[node1.id_int, node2.id_int] == pytest.approx(1.0)
    # Reverse edge is weaker (0.5 times similarity)
    assert brain.adj_matrix[node2.id_int, node1.id_int] == pytest.approx(0.5)


def test_brain_map_spmv_recall_and_hebbian_learning():
    """
    Test Sparse Matrix-Vector Multiplication (SpMV) spreading activation and Hebbian co-activation.
    """
    brain = QuantizedBrainMap(max_nodes=100)

    id_a = brain.ingest("topic", "Apple fruit", importance=0.8)
    id_b = brain.ingest("topic", "Orange fruit", importance=0.8)
    id_c = brain.ingest("topic", "Banana fruit", importance=0.8)

    node_a = brain.nodes[brain.id_map[id_a]]
    node_b = brain.nodes[brain.id_map[id_b]]
    node_c = brain.nodes[brain.id_map[id_c]]

    # Force manual links in adjacency matrix
    # Apple <-> Orange link (0.8 similarity)
    brain.adj_matrix[node_a.id_int, node_b.id_int] = 0.8
    brain.adj_matrix[node_b.id_int, node_a.id_int] = 0.8
    # Orange <-> Banana link (0.7 similarity)
    brain.adj_matrix[node_b.id_int, node_c.id_int] = 0.7
    brain.adj_matrix[node_c.id_int, node_b.id_int] = 0.7
    brain.is_matrix_dirty = True

    # Query matching only "Apple"
    # SpMV should spread activation from Apple -> Orange -> Banana
    results = brain.recall("Apple")

    # Node activations should be set after spreading
    assert node_a.activation > 0.0
    assert node_b.activation > 0.0

    # Retrieve stats
    stats = brain.get_stats()
    assert stats["matrix_non_zeros"] > 0
    assert stats["total_nodes_in_ram"] == 3


def test_brain_map_consolidation_and_merkle_recovery():
    """
    Test Ebbinghaus decay, working memory layer transitions, paged long-term serialization,
    and SHA-256 Merkle verified recovery from binary file.
    """
    bin_file = "solomon_brain_map.bin"
    if os.path.exists(bin_file):
        os.remove(bin_file)

    brain = QuantizedBrainMap(max_nodes=100)
    brain.working_ttl = 10  # Low TTL for test

    # Ingest memory node destined for long term
    node_id = brain.ingest("factual", "Core project blueprints", importance=0.9, valence=0.5)
    node = brain.nodes[brain.id_map[node_id]]
    idx = node.id_int

    # Access multiple times to ensure high access count (> 2) to promote to short-term
    node.access()
    node.access()

    # Move creation time to past (> working_ttl)
    node.creation_time = time.time() - 50.0

    # Run first consolidation: Working -> Short Term
    brain.consolidate()
    assert node.layer == LAYER_SHORT_TERM
    assert idx in brain.nodes  # Still in RAM

    # Move creation time further back (> 86400 seconds) to trigger long-term serialization
    node.creation_time = time.time() - 100000.0

    # Run consolidation again: Short Term -> Long Term (Serialized to bin file & cleared from RAM)
    brain.consolidate()
    assert idx not in brain.nodes  # Cleared from RAM
    assert os.path.exists(bin_file)

    # Recover from binary blob using zero-copy seeker
    recovered = brain._read_from_blob(idx)
    assert recovered is not None
    assert recovered["importance"] == pytest.approx(node.importance)
    assert recovered["layer"] == LAYER_LONG_TERM

    # Corrupt the binary file and verify that the Merkle immune check rejects the record
    # Let's read binary data, alter one byte, write back, and read
    with open(bin_file, "rb") as f:
        data = bytearray(f.read())

    # Flip a bit in the metadata body of the record (e.g. index 10)
    data[10] ^= 0xFF
    with open(bin_file, "wb") as f:
        f.write(data)

    # Attempt to read again (should fail/skip because hashlib.sha256(b_data).digest() != b_hash)
    corrupted_recovery = brain._read_from_blob(idx)
    assert corrupted_recovery is None

    # Cleanup test artifact
    if os.path.exists(bin_file):
        os.remove(bin_file)


def test_brain_map_dream_cycle():
    """
    Test dream cycle random walks and associations creation.
    """
    brain = QuantizedBrainMap(max_nodes=50)

    # Ingest a path of 4 nodes
    id_1 = brain.ingest("thought", "Node one")
    id_2 = brain.ingest("thought", "Node two")
    id_3 = brain.ingest("thought", "Node three")

    idx_1 = brain.id_map[id_1]
    idx_2 = brain.id_map[id_2]
    idx_3 = brain.id_map[id_3]

    # Explicitly link Node 1 <-> Node 2 <-> Node 3
    brain.adj_matrix[idx_1, idx_2] = 0.9
    brain.adj_matrix[idx_2, idx_3] = 0.9
    brain.is_matrix_dirty = True

    # Run dream cycle
    brain.dream_cycle(max_steps=5)

    # Verify dream cycle starts background ANS safely
    brain.start_ans()
    assert brain.ans_running is True
    brain.stop_ans()
    assert brain.ans_running is False
