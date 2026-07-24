# 5-Year Quantization Roadmap for Project Solomon

## Current State (Year 1)
- Dynamic 8-bit and 4-bit loading via `QuantizationCore`.
- VRAM-aware context budgeting with `DynamicContextEngine`.
- Foundational `UnifiedEmbeddingEngine` integrating basic quantization natively.

## Emerging Techniques (Year 2-3)
- **Quantized Embeddings:** Moving from FP32 cosine similarity to native INT4/binary Hamming distance metrics.
- **Mixed Precision Graphs:** Graph nodes storing self-compressed ternary weights.
- **Speculative Decoding Simulators:** Multi-tenant Paged KV-Cache handling.

## Future Hardware & Breakthroughs (Year 4-5)
- **1-bit Architectures:** Widespread integration of BitNet (b1.58) mechanics directly into the local AI stack, bypassing matrix multiplication entirely.
- **On-chip Learning:** Leveraging neuromorphic architectures where the Perpetual Learning pipeline updates weights dynamically without full backprop.
