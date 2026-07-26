from solomon_quantized_memory import QuantizedMemoryNode

def consolidate_memory():
    # Simulate saving fact_memory about the 80/90 layout
    node = QuantizedMemoryNode(
        node_type="fact_memory",
        content={"action": "locked_threshold_logic", "thresholds": [80, 90], "aesthetic": "biological_persistence"},
        importance=1.0,
        valence=0.8
    )

    # Layer 2 is long-term memory
    node.layer = 2
    print(f"Memory Consolidated: {node.id_str} in Layer {node.layer} for {node.content}")

if __name__ == "__main__":
    consolidate_memory()
