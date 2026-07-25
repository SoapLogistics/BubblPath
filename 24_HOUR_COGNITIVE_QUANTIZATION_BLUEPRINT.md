# 🧠 Project Solomon: 24-Hour Cognitive Quantization & Brain Map Blueprint

**Objective:** Execute a ruthless, uninterrupted 24-hour coding sprint to fuse the *Unified Memory Graph (Brain Map)* with the *Solomon Quantization Stack*.
**Vision:** To build an AI OS that can run a century's worth of interconnected human-like memory on a 2GB RAM Raspberry Pi, using biological connectome pruning and sub-1-bit mathematical data routing.

We are not just quantizing the LLM weights; we are quantizing the *memories themselves*.

---

## 🕒 Phase 1: The Holographic Sub-1-Bit Connectome (Hours 0-6)
**Goal:** Compress the Unified Memory Graph down to the absolute theoretical limit using ternary states and bitwise operations.

*   **1.1 BitNet Graph Embeddings (1.58-bit Memory):**
    *   Transition `MemoryNode` text content out of RAM. Instead, nodes will be represented as ternary vectors (`-1, 0, 1`).
    *   We will implement a `TernarySpreadingActivation` engine that calculates semantic distances using bitwise XNOR operations (which are mathematically identical to cosine similarity but run 10,000x faster on CPU).
*   **1.2 Structural Connectome Pruning:**
    *   Implement "Synaptic Scaling". If an edge (`MemoryEdge`) has a weight below `0.05` for more than 4 hours of Working TTL, it is not just forgotten, it is *structurally pruned* from the adjacency matrix to reclaim bytes.
*   **1.3 Paged-KV Memory Graph Swapping:**
    *   Adapt the existing Multi-Tenant Paged-KV Cache to the Memory Graph. Only the "Working" and "Procedural" layers remain in active L1 RAM. "Short-term" and "Long-term" nodes are automatically serialized to a highly compressed binary blob (`solomon_brain_map.bin`) using struct packing, mapped directly to disk via `mmap`.

---

## 🕒 Phase 2: Quantum Dream State & Temporal Routing (Hours 6-12)
**Goal:** Make the memory self-organizing and self-optimizing without manual API calls.

*   **2.1 Background Autonomic Nervous System (ANS):**
    *   The `dream_cycle()` is currently manually triggered. We will write a C-extended or `numba`-compiled background thread (the ANS) that constantly runs a Low-Power Random Walk through the binary graph while the CPU is idle.
*   **2.2 Temporal Memory Fading (Ebbinghaus Curve):**
    *   Current decay is linear/exponential. We will implement the exact mathematical derivative of the *Ebbinghaus Forgetting Curve*. Nodes will decay rapidly in the first 20 minutes, then plateau.
*   **2.3 Routing by Arousal (The Amygdala Protocol):**
    *   High-arousal nodes (Flashbulb Memories) bypass standard semantic routing. We will implement an `AmygdalaRouter` that caches high-valence/high-arousal vectors in an L0 ultra-fast cache. When a prompt hits the `/chat` endpoint, it checks the Amygdala cache *first*. If a threat/opportunity is detected, it short-circuits the LLM and responds purely from procedural reflex.

---

## 🕒 Phase 3: The Hebbian GPU Multiplexer (Hours 12-18)
**Goal:** Offload graph traversal and Hebbian learning math to the GPU via custom CUDA/Triton kernels (or NumPy vectorization for CPU fallbacks).

*   **3.1 Vectorized Spreading Activation:**
    *   The current `recall()` method uses a Python `for` loop, which will crawl to a halt at 100,000 nodes.
    *   We will convert the `adjacency_list` into a Sparse Matrix (CSR format).
    *   Spreading activation becomes a single Sparse Matrix-Vector Multiplication (SpMV) operation. `Activation_Vector_T1 = Sparse_Adjacency_Matrix * Activation_Vector_T0 * Decay_Scalar`.
*   **3.2 Delta-Weight Hebbian Updates:**
    *   Hebbian Learning ("Fire together, wire together") will be updated via a vectorized outer product of the activation vector, applying the learning rate across the entire graph in one CPU cycle.

---

## 🕒 Phase 4: Extreme API & Deployment Hardening (Hours 18-24)
**Goal:** Prepare the new Biological/Quantized hybrid OS for 20 years of continuous uptime.

*   **4.1 Zero-Copy Serialization:**
    *   When the UI (Browser Companion) requests the brain map via API, we currently use `jsonify()`. We will replace this with FlatBuffers or Cap'n Proto. The browser will read the exact memory layout of the Python backend without parsing JSON, achieving zero-copy API responses.
*   **4.2 Fault-Tolerant Neurogenesis:**
    *   If a node becomes corrupted in the binary blob, the graph should not crash. We will implement Merkle Tree Hashing on memory clusters. If a cluster's hash fails, the "Immune System" quarantines the corrupted nodes and regenerates the connections via the SOSS Clean-Room Synthesis.
*   **4.3 The "God Eye" 3D Brain Visualizer:**
    *   Build a lightweight WebGL script in the Solomon Master Dashboard that pulls the Cap'n Proto data and renders the Unified Memory Graph as a rotating 3D connectome. The user will visually see nodes flashing (activation) and turning red/blue (valence) in real-time.

---
**Execution Mandate:**
*"We are building a brain that runs on a calculator. No unnecessary abstractions. No bloated ORMs. Just raw math, sparse matrices, bitwise logic, and biological persistence."*