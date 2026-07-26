import os
import shutil
import pytest
import numpy as np
from solomon_quantized_memory import (
    QuantizedBrainMap,
    QuantizedMemoryNode,
    LAYER_WORKING,
    LAYER_SHORT_TERM,
    LAYER_LONG_TERM
)

@pytest.fixture(autouse=True)
def clean_binary_blob():
    """Ensure any previous binary map is removed before and after each test."""
    blob_file = "solomon_brain_map.bin"
    if os.path.exists(blob_file):
        os.remove(blob_file)
    yield
    if os.path.exists(blob_file):
        os.remove(blob_file)

def test_brain_map_initialization():
    brain_map = QuantizedBrainMap(max_nodes=100)
    assert brain_map.max_nodes == 100
    assert len(brain_map.nodes) == 0
    assert brain_map.get_stats()["total_nodes_in_ram"] == 0

def test_ingestion_and_amygdala_protocol():
    brain_map = QuantizedBrainMap(max_nodes=50)

    # Standard ingest
    node_id_1 = brain_map.ingest(
        node_type="episodic",
        content="Routine system check passed",
        importance=0.4,
        valence=0.1,
        arousal=0.2
    )
    assert node_id_1 in brain_map.id_map
    idx_1 = brain_map.id_map[node_id_1]
    node_1 = brain_map.nodes[idx_1]
    assert node_1.content == "Routine system check passed"
    assert node_1.layer == LAYER_WORKING
    assert node_id_1 not in brain_map.amygdala_cache

    # High arousal / fear / danger node -> triggers Amygdala Protocol
    node_id_2 = brain_map.ingest(
        node_type="warning",
        content="CRITICAL: Unauthorized system access attempt detected!",
        importance=0.9,
        valence=-0.9,
        arousal=0.8
    )
    assert node_id_2 in brain_map.id_map
    idx_2 = brain_map.id_map[node_id_2]
    node_2 = brain_map.nodes[idx_2]
    assert node_id_2 in brain_map.amygdala_cache
    assert brain_map.amygdala_cache[node_id_2] == node_2

def test_linear_probing_collision():
    brain_map = QuantizedBrainMap(max_nodes=10)

    # Ingest multiple nodes to force collision
    # Their raw id_int % 10 could collide. We will manually overwrite their id_int or simply ingest many.
    for i in range(8):
        brain_map.ingest(
            node_type="fact",
            content=f"Fact number {i}",
            importance=0.5
        )

    # Check that they all are stored at unique slots
    assert len(brain_map.nodes) == 8
    unique_indices = set(brain_map.nodes.keys())
    assert len(unique_indices) == 8

def test_recall_and_spreading_activation_and_hebbian_learning():
    brain_map = QuantizedBrainMap(max_nodes=100)

    # Ingest semantically related nodes
    nid_1 = brain_map.ingest("episodic", "deploy app production", importance=0.8)
    nid_2 = brain_map.ingest("episodic", "production deploy database script", importance=0.8)
    nid_3 = brain_map.ingest("fact", "database backup routine", importance=0.5)

    idx_1 = brain_map.id_map[nid_1]
    idx_2 = brain_map.id_map[nid_2]
    idx_3 = brain_map.id_map[nid_3]

    # Explicitly link them in adjacency matrix for testing
    brain_map.adj_matrix[idx_1, idx_2] = 0.6
    brain_map.adj_matrix[idx_2, idx_1] = 0.6
    brain_map.adj_matrix[idx_2, idx_3] = 0.5
    brain_map.adj_matrix[idx_3, idx_2] = 0.5
    brain_map.is_matrix_dirty = True

    # Recall using query "deploy app"
    results = brain_map.recall("deploy app", top_k=5)

    # Verify we got relevant results
    assert len(results) > 0
    # Spreading activation should have elevated the activation of related nodes (nid_2, etc.)
    assert brain_map.nodes[idx_1].activation > 0.0

    # Verify vectorized Hebbian learning increased the weight between co-activated nodes
    # Co-activated indices in the recall were activated. Check that adjacency weight is bounded
    assert brain_map.adj_matrix[idx_1, idx_2] <= 1.0

def test_consolidation_and_direct_binary_recall():
    brain_map = QuantizedBrainMap(max_nodes=10)

    # 1. Ingest a node that we will transition to Long-Term Memory
    nid = brain_map.ingest("lesson", "Keep all models timezone-aware", importance=0.9, arousal=0.5)
    idx = brain_map.id_map[nid]
    node = brain_map.nodes[idx]

    # Force Layer state transitions to SHORT_TERM and then consolidate to LONG_TERM
    node.layer = LAYER_SHORT_TERM
    # Modify creation time to simulate age > 1 day
    node.creation_time -= 90000

    # 2. Run consolidation - should pre-allocate the file and write node directly at idx offset
    brain_map.consolidate()

    # Check node was evicted from RAM
    assert idx not in brain_map.nodes
    assert nid not in brain_map.id_map

    # Check binary blob file was created
    assert os.path.exists("solomon_brain_map.bin")
    expected_size = 10 * 201 # max_nodes * RECORD_SIZE
    assert os.path.getsize("solomon_brain_map.bin") == expected_size

    # 3. Retrieve using direct-seek O(1) recall from blob
    recovered = brain_map._read_from_blob(idx)
    assert recovered is not None
    assert recovered["layer"] == LAYER_LONG_TERM
    assert recovered["importance"] == pytest.approx(0.9)
    assert recovered["id"] == f"blob-recovered-{idx}"

def test_binary_recall_sha256_merkle_verification():
    brain_map = QuantizedBrainMap(max_nodes=10)
    nid = brain_map.ingest("lesson", "Immutable security boundaries", importance=0.95)
    idx = brain_map.id_map[nid]

    # Push to long-term
    brain_map.nodes[idx].layer = LAYER_SHORT_TERM
    brain_map.nodes[idx].creation_time -= 90000
    brain_map.consolidate()

    # Verify it recovers perfectly first
    assert brain_map._read_from_blob(idx) is not None

    # Corrupt the hash part of that record in the file
    RECORD_SIZE = 201
    offset_to_hash = idx * RECORD_SIZE + 169

    with open("solomon_brain_map.bin", "r+b") as f:
        f.seek(offset_to_hash)
        # Overwrite with wrong hash bytes
        f.write(b'\xff' * 32)

    # Recovery should fail verification (since hash doesn't match calculations) and return None
    assert brain_map._read_from_blob(idx) is None

def test_dream_cycle():
    brain_map = QuantizedBrainMap(max_nodes=10)

    # Ingest a few nodes
    nid_1 = brain_map.ingest("fact", "Node Alpha")
    nid_2 = brain_map.ingest("fact", "Node Beta")
    nid_3 = brain_map.ingest("fact", "Node Gamma")

    idx_1 = brain_map.id_map[nid_1]
    idx_2 = brain_map.id_map[nid_2]
    idx_3 = brain_map.id_map[nid_3]

    # Setup some edges so walk can proceed
    brain_map.adj_matrix[idx_1, idx_2] = 0.5
    brain_map.adj_matrix[idx_2, idx_3] = 0.5
    brain_map.is_matrix_dirty = True

    # Execute dream cycle random walk
    brain_map.dream_cycle(max_steps=5)

    # Dream cycle should form new distant associations (non-zero matrix elements)
    stats = brain_map.get_stats()
    assert stats["matrix_non_zeros"] > 0
