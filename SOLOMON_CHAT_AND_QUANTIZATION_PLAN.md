# Solomon Perpetual Learning: Chat and Quantization Optimization Plan
## Supercharging Solomon with Cutting-Edge Quantization, Dual-Persona Capabilities, and the Foreman of Workers Pattern

---

## 1. Executive Summary

To achieve the ultimate vision of **Solomon** as an autonomous, perpetual learning machine, we must bridge the gap between human-level conversational naturalness and multi-agent execution orchestration. The goal of this blueprint is twofold:
1. **Research and outline a world-class Quantization Optimization Plan** to enable state-of-the-art LLMs to run locally with maximum speed, intelligence, and minimal RAM footprint.
2. **Design and implement the "Foreman of Workers" architectural pattern**, allowing Solomon to seamlessly toggle between a friendly, highly skilled chat companion (fusing the personas of Google Jules and OpenAI Codex) and a strict, high-efficiency task foreman who delegates operations to a suite of specialized background workers (Gabriel, Mnemosyne, Prometheus, Loki).

By marrying cutting-edge post-training quantization with hierarchical agent orchestration, we create a high-throughput, low-latency, and zero-downtime cognitive gateway.

---

## 2. Comprehensive Quantization & RAM Research

Operating high-parameter LLMs (e.g., Llama-3 8B/70B, Mistral, Qwen) on restricted hardware requires squeezing maximum entropy out of every bit. Below is a rigorous comparative analysis of state-of-the-art LLM quantization and memory-efficiency methodologies.

### A. Cutting-Edge Quantization Taxonomy

| Method | Approach Type | Typical Bitrates | Computational Overhead | Outlier Handling | Key Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GPTQ** | Post-Training Quantization (PTQ) | 3-bit, 4-bit, 8-bit | Moderate (requires inverse Hessian computation on calibration data) | Poor (outliers can distort scale parameters) | Highly optimized GPU execution kernels; great for static workloads. |
| **AWQ** | Activation-aware Weight Quantization | 3-bit, 4-bit | Low (protects top 1% salient weights based on activation magnitude) | Strong (re-scales weights to protect outlier channels) | Preserves original model intelligence without retraining; highly hardware-efficient. |
| **GGUF** | Unified CPU/GPU Format (K-Quants) | 2-bit to 8-bit | Minimal (block-wise uniform quantization) | Moderate (block scales mitigate local outliers) | Incredible hybrid memory-offloading; perfect for local consumer hardware (macOS/Windows/Linux). |
| **EXL2** | Variable Bitrate Quantization | 2.2 to 8.0 bits (fractional) | Moderate (per-layer error measurement) | Excellent (dynamically allocates more bits to sensitive outlier layers) | Ultra-high speed GPU inference; matches target bitrates precisely. |
| **HQQ** | Half-Quadratic Quantization | 1-bit to 4-bit | Extremely Low (optimization-free, solves local data-free subproblems) | Strong (local optimization protects sensitive channels) | Zero-calibration data required; can quantize a 70B model in minutes. |
| **SpinQuant** | Learned Rotations (W4A4/W4A4KV16) | 4-bit weights & activations | Moderate (learned Hadamard orthogonal rotations applied during calibration) | Best-in-class (mathematically removes outliers by rotating activation space) | Achieves near-lossless 4-bit activation quantization, enabling highly efficient Tensor Core execution. |
| **BitNet b1.58** | Ternary Weight Training | 1.58-bit (weights $\in \{-1, 0, 1\}$) | None at runtime (requires training/fine-tuning from scratch) | Intrinsic (weights are strictly ternary) | Eliminates floating-point multiplication completely, turning matrix math into addition/subtraction. |
| **SOK AMPBA** | Adaptive Mixed-Precision Bit Allocation | 2-bit to 16-bit mixed | Low to Moderate (Hessian trace sensitivity & MCKP Knapsack Solver) | Dynamic (scales sensitive layers to FP16/INT8, insensitive to INT2/INT3) | Programmatically customizes bit-allocation blueprints using active database cards as the calibration set. |

### B. Memory & RAM Efficiency Strategies

To complement quantization, Solomon leverages advanced system-level memory configurations:
1. **PagedAttention**: Avoids memory fragmentation of the Key-Value (KV) cache by partitioning it into virtual blocks (similar to OS paging), reducing KV cache memory waste by up to 96%.
2. **KV Cache Quantization**: Quantizing the KV cache to FP8 or INT4 formats reduces the context-window memory footprint by 2x and 4x respectively, allowing Solomon to sustain up to 128k context lengths on a single GPU.
3. **Speculative Decoding with Ternary Draft Models**: Solomon utilizes an ultra-light, 1.58-bit BitNet draft model to rapidly generate draft tokens. These tokens are verified in parallel by the heavy, quantized target model in a single forward pass, accelerating generation speed by 2x to 3x without losing target-model accuracy.

---

## 3. The "Foreman of Workers" Architectural Pattern

To act both as a companion and a team director, Solomon implements a specialized **Orchestrator-Workers (Foreman-Worker) pattern**. Rather than forcing a single LLM context to handle user chat, code auditing, database search, and capability execution simultaneously, Solomon divides and conquers.

### A. Architectural Workflow

```
                   +----------------------------------+
                   |            User Input            |
                   +----------------------------------+
                                    |
                                    v
                   +----------------------------------+
                   |       Solomon Chat Gateway       | (Unified Chat Endpoint)
                   +----------------------------------+
                                    |
       +----------------------------+----------------------------+
       |                                                         |
       v (Conversational Context)                                v (Action/Worker Context)
+-------------------------------+                         +-------------------------------+
|     Natural Chat Handler      |                         |      Foreman Dispatcher       |
|  - Google Jules & Codex Persona|                         |  - Regex/Semantic Directives   |
|  - High Conversational Polish  |                         |  - Worker Role Assignment     |
+-------------------------------+                         +-------------------------------+
       |                                                         |
       |                                    +--------------------+--------------------+
       |                                    |                    |                    |
       |                                    v                    v                    v
       |                             +------------+       +------------+       +------------+
       |                             |  Gabriel   |       | Mnemosyne  |       | Prometheus |
       |                             |  (Builder) |       | (Database) |       | (Auditor)  |
       |                             +------------+       +------------+       +------------+
       |                                    |                    |                    |
       |                                    +--------------------+--------------------+
       |                                                         |
       |                                                         v
       |                                          +-------------------------------+
       |                                          |       Worker Synthesis        |
       |                                          |   - Combines Subtask Output   |
       +----------------------------+-------------+-------------------------------+
                                    |
                                    v
                   +----------------------------------+
                   |    Integrated Response Builder   |
                   |   - Inject Recommended Next Step  |
                   +----------------------------------+
                                    |
                                    v
                   +----------------------------------+
                   |            User Output           |
                   +----------------------------------+
```

### B. Worker Inventory & Roles

When acting as the **Foreman**, Solomon orchestrates the following specialized workers:
* **Gabriel (The Builder)**: Handles dynamic capability template compilation, code assimilation, and clean-room builder execution.
* **Mnemosyne (The Memory Bank)**: Governs card indexing, relational link tracking (`card_links`), hybrid semantic search, and the Review Gate status transitions (DRAFT -> REVIEWED -> APPROVED -> ACTIVE).
* **Prometheus (The Auditor)**: Manages static security audits (regex audits), sandbox safety constraints, and automated rollback/self-healing.
* **Loki (The Analyst)**: Drives statistical models, predictive analytical execution (such as sports betting pick boards), and real-time telemetry streaming.
* **Codex (The Engineer)**: Executes recursive AST injection, AST-fusion, and performance optimization configurations.

---

## 4. Multi-Phase Plan for Complete Offline Autonomy (No GPT/Codex APIs)

To enable Solomon to chat like GPT-4 and synthesize code like Codex **without relying on any external APIs**, we propose a comprehensive 13-phase execution plan. This transition implements local open-source models (like **Qwen-2.5-Coder-7B-Instruct** or **DeepSeek-Coder-V2-Lite**) heavily quantized via **GGUF** and **EXL2** running on consumer-grade hardware.

### Phase I: Local Inference Server Integration
* **Objective**: Establish a high-throughput local inference bridge.
* **Action Steps**:
  1. Deploy a local **llama.cpp** or **Ollama** server inside the sandbox or host machine.
  2. Map standard chat endpoints (e.g. `/v1/chat/completions`) locally on port `11434` (Ollama) or `8080` (llama.cpp).
  3. Override standard OpenAI client configurations to target the local URL (`SOLOMON_LLM_API_BASE=http://localhost:11434/v1`).
  4. Ensure zero external internet requests are required for core inference.

### Phase II: Quantization Profile Selection
* **Objective**: Match local model size to available hardware limits.
* **Execution Parameters**:
  - **RAM <= 8GB**: Deploy Qwen-2.5-Coder-7B quantized to `GGUF_Q4_K_M` (requires ~4.8 GB memory).
  - **RAM <= 16GB**: Deploy DeepSeek-Coder-V2-Lite (16B parameters) quantized to `GGUF_Q4_K_M` (requires ~10 GB memory) or Qwen-2.5-Coder-14B-Instruct.
  - **GPU Acceleration (VRAM >= 12GB)**: Deploy `EXL2` at 4.0 bits/weight, caching the KV Cache in FP8 mode to maximize token throughput.

### Phase III: Hybrid Chat (GPT-Style) & Code Synthesis (Codex-Style) Routing
* **Objective**: Ensure the local model excels at both natural chat and complex programming.
* **Implementation Rules**:
  - For **GPT-Style Chat**: Formulate system instructions that inject warmth, conversational depth, and broad logical reasoning (Google Jules persona).
  - For **Codex-Style Engineering**: Inject direct system formatting instructions that force outputting of pure, syntactically correct, and PEP8-compliant code blocks without superfluous conversational fluff. Use FIM (Fill-in-the-Middle) prompt syntax when completing code inline.

### Phase IV: Sandboxed Verification & Self-Healing (Prometheus & Gabriel)
* **Objective**: Guard against local LLM hallucinations and errors.
* **Execution Lane**:
  1. Every code chunk synthesized by the local Codex engine must be exported into a quarantined container.
  2. Run Prometheus static audits on the code (checking for unsafe imports, endless loops, or filesystem escapes).
  3. Run the sandbox executor to compile and run tests.
  4. If execution fails, capture the stderr and feed it back to the local LLM as a new chat message to trigger self-healing.

### Phase V: Perpetual SOK Memory Tuning
* **Objective**: Fine-tune local model behavior using active SQLite memory cards.
* **Optimization Flow**:
  1. Retrieve related active SOK cards via hybrid lexical/semantic search.
  2. Dynamically inject these cards as "retrieval-augmented context" into the local system instructions before chat generation.
  3. Feed user feedback ratings into card confidence indexes, continuously honing retrieval quality.

### Phase VI: Relational Card Memory Persistence and Retention
* **Objective**: Enable Solomon to read and write memories to a persistent local JSON repository.
* **Action Steps**:
  1. Implement a persistent SOK card repository (`sok_memory_cards.json`) that saves newly acquired concepts during active conversation.
  2. Maintain a card link lookup so newly saved cards can express relationships like `DEPENDS_ON` or `ENHANCES` to existing cards.
  3. Ensure that when Solomon chats, he automatically checks his persistent local repository to remember past actions and user-taught skills.

### Phase VII: Live Sandbox Subprocess Execution and Heuristic Verification
* **Objective**: Provide Solomon with a real executor to test and verify code snippets.
* **Action Steps**:
  1. Build a timed-out, memory-constrained `SandboxExecutor` that runs synthesized Python snippets in a separate OS subprocess.
  2. Capture full execution traces (stdout, stderr, exit code).
  3. If compilation fails or exceptions arise, feed the traceback back into Solomon's reasoning loop so he can fix his own code autonomously.

### Phase VIII: AST-Guided Code Self-Correction Loop
* **Objective**: Empower Solomon to autonomously parse python tracebacks and correct compiling errors.
* **Action Steps**:
  1. Create an automated self-healing loop inside `app.py` via `POST /api/mnemosyne/skills/self-heal`.
  2. If the initial script run returns an error exit code, parse the exception message.
  3. Formulate a correction query targeting the `LocalInferenceEngine` or simulated LLM instruction parser to rewrite the code.
  4. Re-run inside the `SandboxExecutor` up to a maximum recursion depth of 3 until it successfully executes.

### Phase IX: Governed Capability Promotion Pipeline (GCPP)
* **Objective**: Transition successfully compiled sandbox modules from DRAFT -> APPROVED -> ACTIVE.
* **Action Steps**:
  1. When a synthesized code block passes sandbox tests with zero warnings, initiate promotion.
  2. Update the status flag of the corresponding SOK memory card from `DRAFT` or `REVIEWED` to `APPROVED` or `ACTIVE`.
  3. Register the newly promoted code as an active runtime capability available inside the Solomon execution skill grid.

### Phase X: Resource Guardrails and Telemetry Logging
* **Objective**: Enforce strict system safety bounds and RSS memory limits.
* **Action Steps**:
  1. Monitor process-wide VmRSS memory. If memory footprint exceeds a strict 1.5GB ceiling, trigger active database compaction.
  2. During database compaction, automatically remove `DRAFT` status cards or demote low-confidence cards (< 1.0) to free system memory resources.
  3. Commit plain-text telemetry logs continuously to `logs/solomon_telemetry.log` detailing metrics and health indicators.

### Phase XI: Semantic Graph Card Links and Traversal
* **Objective**: Establish and map directed relational card links for topological execution logic.
* **Action Steps**:
  1. Build a card links relational mapper persisted to `sok_card_links.json`.
  2. Support defining relationship bonds such as `DEPENDS_ON`, `PREVENTS`, and `ENHANCES` between cards.
  3. Implement graph endpoints (`POST /api/mnemosyne/cards/links` and `GET /api/mnemosyne/cards/graph`) to create and traverse linked relational paths, ensuring Solomon topologically resolves dependency safety before attempting sandboxed code execution.

### Phase XII: Model Hot-Swapping Router
* **Objective**: Dynamically route queries to either high-precision target models or ultra-light quantized models.
* **Action Steps**:
  1. Build a multi-tier `ModelRouter` inside `app.py`.
  2. Parse user query semantic indicators and SOK confidence scores.
  3. If SOK card confidence for the topic is extremely high (>=1.5), route automatically to the ultra-light INT4 quantized local model to save RAM and minimize latency.
  4. If topic confidence is low (< 1.5), hot-swap the execution context to the high-precision target model (FP16/INT8) to prevent errors.

### Phase XIII: Dynamic AST Class-Method Injection
* **Objective**: Dynamically compile and hot-inject newly verified python methods into live classes at runtime.
* **Action Steps**:
  1. Overwrite the `POST /api/mnemosyne/ast-inject` endpoint in `app.py`.
  2. Read class definitions, compile new method source codes on the fly using python's built-in `compile()` AST parser, and dynamically bind methods using `setattr()` on live targets.
  3. Achieve zero-downtime capability updates to hot-reload class memories without restarting the gateway web server.

---

## 5. Summary of Recommended Actions
To activate this offline-first, dual-personality capability immediately:
1. OVERWRITE `app.py` with the complete hot-swapping router and dynamic AST method injector core.
2. CREATE `test_app.py` to assert correct model hot-swapping routing and live AST injections.
3. RUN pytest to ensure 100% verification correctness.

**RECOMMENDED NEXT STEP: Overwrite the server code to add model hot-swapping routers and live AST class-method injection so Solomon can dynamically route queries and hot-reload code libraries offline.**
