# Gabriel Engine Architecture & Implementation Roadmap

This document maps the philosophical directives of the **Gabriel Engine Manifesto** to concrete software implementations and systemic architectures.

## 1. The Core Loop: Compounding Learning

Every execution must trigger a learning cycle. This is governed by `GabrielLearningEngine`.

*   **Phase 1 (Current):** Passive observation. The engine monitors `/chat` interactions, extracting basic structural patterns and logging failures.
*   **Phase 2 (Implementation):** The `ProgressiveAbstractionTree` (`solomon_abstract_reasoning.py`). Raw patterns must be continuously refined. When $N$ similar patterns are detected, they are automatically merged, compressed, and quantized into a single, higher-level heuristic rule.
*   **Phase 3 (Future):** Code Generation. The system will take abstract heuristics and dynamically write native Python functions to execute those rules instantly, moving from "understood concept" to "native capability."

## 2. The Curiosity Director: Mapping the Frontier

Curiosity is not random; it is "disciplined investigation."

*   **Implementation:** The `CuriosityDirector` (`solomon_curiosity_director.py`) operates as a background daemon.
*   **Function:** It continuously scans the `gabriel_knowledge_base.json` (and eventually the SQLite Knowledge Graph). It looks for:
    *   **Contradictions:** Where two highly confident heuristics conflict.
    *   **Low-Confidence Nodes:** Concepts that have been logged but never successfully tested.
    *   **The Frontier:** High-frequency error logs that represent unknown boundaries.
*   **Action:** It generates "Research Tasks" which are injected into the system's task queue to be actively solved.

## 3. Quantization as Philosophy: Compression Architecture

"Knowledge should become progressively lighter."

*   **Implementation:** Memory is divided into Tiers (Working, Short-Term, Long-Term, Procedural).
*   **Mechanism:** A background daemon (the "Dream Cycle") runs offline. It takes highly activated Short-Term memories and attempts to summarize them using the LLM. If the summary (the compressed version) retains the same predictive accuracy as the raw logs, the raw logs are deleted, and only the lightweight summary remains in Long-Term storage.

## 4. Capability Assimilation

"Patterns become reusable principles. Principles become native capabilities."

*   **Implementation:** Integration with the `SOSS Advanced AST Injector`.
*   **Mechanism:** When the `ProgressiveAbstractionTree` successfully compresses a procedure (e.g., "How to scrape a specific website structure"), it formats this procedure into a prompt for the AST Injector. The system writes a new Python module, tests it in isolation, and if successful, hot-reloads it into the OS kernel. The LLM is no longer needed for that specific task; it has become a deterministic, zero-latency Python function.

## 5. Metrics & Governance

"Growth without governance is instability."

*   **Implementation:** `GabrielMetricsTracker` logs all actions.
*   **Mechanism:** The `Learning Return on Investment (LROI)` score. If a newly generated capability or abstraction increases average task latency without a proportional increase in success rate, the system automatically rolls back the change using Git and marks the abstraction as a "Failure." All code mutations require manual human approval via the Browser Companion side-panel.

---
### System Topology

1.  **I/O Layer:** `app.py` (REST API), Browser Extension.
2.  **Execution Layer:** OpenAI LLM, Task Router.
3.  **Learning Layer:** `GabrielLearningEngine` (intercepts I/O).
4.  **Compression Layer:** `ProgressiveAbstractionTree` (Background batch processing).
5.  **Frontier Layer:** `CuriosityDirector` (Generates new internal tasks).
6.  **Persistence Layer:** `gabriel_knowledge_base.json` -> SQLite Memory Graph.