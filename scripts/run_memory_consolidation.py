import sys
import os

try:
    from core.solomon_quantized_memory import QuantizedBrainMap
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.solomon_quantized_memory import QuantizedBrainMap

def consolidate_futures_memory():
    print("Initializing QuantizedBrainMap for Futures consolidation...")
    brain = QuantizedBrainMap(max_nodes=100)

    # Simulate ingesting the layout and threshold logic as permanent fact_memory
    print("Ingesting Futures layout and threshold logic as permanent fact_memory...")
    brain.ingest(
        node_type="fact_memory",
        content="Futures Engine 80/90 threshold logic is strictly audited, deterministic, and bound to data_health shape.",
        importance=1.0,
        valence=0.0,
        arousal=0.0
    )

    brain.ingest(
        node_type="fact_memory",
        content="Futures Dashboard visual layout and data binding implemented. Governance refusal handling integrated.",
        importance=0.9,
        valence=0.0,
        arousal=0.0
    )

    print("Running memory consolidation cycle...")
    brain.consolidate()
    print("Memory consolidation complete.")

if __name__ == "__main__":
    consolidate_futures_memory()
