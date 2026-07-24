# Architecture Decision Record: Phase 1 - Dynamic Context and Pluggable Embeddings

## Status
Adopted

## Context
Project Solomon needed to move away from rigid 4,000-character retrieval limits and deterministic hashing-based search logic to more robust, semantically meaningful relationships while enforcing hard resource bounds. The context system must intelligently prioritize the most critical information within a dynamic budget, and the embedding system must support dense model embeddings while retaining an offline degraded fallback.

## Decisions

### 1. Pluggable Embedding Architecture
- Introduced an `EmbeddingProvider` abstract base class to separate embedding generation from database retrieval logic.
- Preserved the existing deterministic SHA-256 hash logic within `DeterministicHashProvider` as a guaranteed fallback.
- Implemented `DenseEmbeddingProvider` utilizing `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to provide high-fidelity semantic meaning.
- Updated `card_embeddings` schema in SQLite to track `provider`, `model`, `vector_dimension`, `model_fingerprint`, and `source_content_hash`.

### 2. Asynchronous Re-embedding Worker
- Created `AsyncEmbeddingWorker` (`solomon_embedding_worker.py`) which runs in a background thread and batches database reads/writes.
- The worker detects newly added or modified cards lacking a dense embedding and computes them asynchronously, avoiding blocking the main API thread.

### 3. Context Budget Planner
- Created `ContextBudgetPlanner` (`solomon_context_budgeter.py`) to replace static bounds.
- It calculates a `budget` by taking the `model_context_window` and subtracting `system_prompt_reserve`, `expected_response_reserve`, `task_input_size`, and a `safety_margin`.
- Memory cards are retrieved in priority layers (Governance/Safety -> Direct Matches -> Failures -> Dependencies -> Optional). Truncation happens precisely when the calculated token budget is met, preventing runaway token usage and context dilution.

## Consequences
- **Positive**: Significantly more accurate semantic retrieval and robust guardrails against API abuse or local model OOM (Out-of-Memory) errors via token budgeting.
- **Positive**: Complete backwards compatibility via fallback routing; legacy database states won't break if `sentence-transformers` is unavailable.
- **Negative**: Adds a heavy dependency (`sentence-transformers` + PyTorch) to the environment. To mitigate, we handle the `ImportError` gracefully, reverting to the fallback.

## Operational Runbook & Rollback Procedure
- **Runbook**: To activate dense embeddings, install `sentence-transformers`. Run `AsyncEmbeddingWorker.start()` upon system initialization.
- **Rollback**: If dense models fail, simply uninstall `sentence-transformers`. `solomon_embeddings.py` will catch the missing module and automatically route all new and query requests to `DeterministicHashProvider`.
