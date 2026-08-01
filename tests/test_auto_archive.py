import time
from core.solomon_quantized_memory import QuantizedBrainMap, QuantizedMemoryNode, LAYER_WORKING, LAYER_SHORT_TERM, LAYER_LONG_TERM

def test_auto_archive_chat():
    memory = QuantizedBrainMap()
    node_id = memory.ingest(node_type="chat_input", content="hello", importance=0.8)

    # Fast forward time
    with memory.nodes_lock:
        node = memory.nodes[memory.id_map[node_id]]
        node.last_accessed = time.time() - 86401  # > 24 hours

    memory.consolidate()

    # Node should be serialized (archived) and removed from RAM
    assert node_id not in [n.id_str for n in memory.nodes.values()]

if __name__ == "__main__":
    test_auto_archive_chat()
    print("Test passed!")
