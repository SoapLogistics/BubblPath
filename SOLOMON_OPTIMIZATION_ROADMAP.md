# Project Solomon: 25-Step Optimization Roadmap

This document outlines 25 specific architectural, performance, and feature optimizations across the SOSS stack, advancing Phase 2 stability and accelerating Phase 3A (Simulation).

### Database & Storage
1. **Enable SQLite WAL Mode:** Switch journaling to Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`) to drastically improve concurrent read/write speed for the background async worker.
2. **Indexing Strategy:** Add indices to `family` and `focus` columns in `knowledge_cards` to speed up category-based pruning.
3. **Canonical Card Protection:** Introduce an `is_canonical` boolean flag. If True, standard agent operations cannot mutate or overwrite the core card without elevated privileges.
4. **Memory Deduplication:** Before upsert, check if a card with > 0.99 cosine similarity exists in the same family. If so, merge relationships rather than polluting the DB with duplicates.
5. **Adaptive Learning Rates:** Canonical anchors are immune to confidence updates, acting as ground truth to prevent system drift.
6. **Maintenance Endpoint:** Expose an API endpoint that safely runs `PRAGMA optimize; VACUUM;` to defragment the SQLite file post-heavy recursive tests.

### Context & Search
7. **LRU Semantic Cache:** Implement `functools.lru_cache` on `compute_local_embedding` and search queries to return instant answers for repeated systemic inquiries.
8. **Hybrid Scoring:** Augment the dense Cosine Similarity score with a lightweight keyword overlap modifier (basic TF-IDF style) to ensure exact matches aren't lost in dense semantic blur.
9. **Dynamic Thresholds:** Modify `ContextBudgetPlanner`. If the token budget is largely unspent, slightly lower the `relevance_threshold` dynamically to fetch wider context.
10. **Auto-Chunking:** In `upsert_card`, if content exceeds 1500 characters, automatically split it into logical chunks to preserve dense embedding accuracy (which degrades on long texts).
11. **Stale Embedding Sweeper:** Add a method to `AsyncEmbeddingWorker` that detects embeddings generated >30 days ago, or by older model hashes, and recalculates them proactively.

### Graph & Topological Resolution
12. **Iterative DFS:** Convert the recursive `dfs` function in `TopologicalResolutionEngine` to an iterative stack loop to prevent Python `RecursionError` on massive knowledge graphs.
13. **Cyclic Self-Healing:** If the Topological engine detects a hard circular loop (`A -> B -> A`), introduce a mechanic to automatically sever the most recently created edge and log the intervention.
14. **Transitive IMPLIES:** Support transitive closure properties. If `A IMPLIES B` and `B IMPLIES C`, automatically weigh `C` in queries involving `A`.
15. **D3.js Visualization Endpoint:** Create `/api/mnemosyne/graph/visualize` returning `{nodes, links}` for frontend topology graphing.

### Security, Routing & Telemetry
16. **Live Budget Routing:** Integrate `ContextBudgetPlanner` into `app.py`'s `/chat` route to actively construct prompt windows using the mathematical boundary limits.
17. **Human-Approval Gate (3B Prep):** Build `solomon_approval_gate.py` that intercepts high-risk graph proposals and flags them as `PENDING_REVIEW` in a SQLite table.
18. **Pre-execution Snapshotting:** Create `DBSnapshotManager` that copies `solomon_mnemosyne_demo.db` to `/tmp` before a Skill Sandbox run, restoring it instantly if the code causes catastrophic cascading failures.
19. **Subprocess Cleanup:** Ensure `SandboxExecutor` (when implemented fully) explicitly tracks and `kill -9`s zombie/orphaned child processes spawned by infinite loops.
20. **Enhanced Telemetry:** Expand `/api/system/health` to report active RAM limits, DB file sizes in MB, async worker backlog queues, and total graph cyclic health.

### Loki Simulation Engine (Phase 3A)
21. **Mock State Simulator:** Build `LokiSimulator` class to track a virtual JSON bankroll without any real-world API keys.
22. **Odds Timestamping:** Record the exact timestamp and implied probability of simulated paper bets to track odds slippage.
23. **ROI & Drawdown Tracker:** Implement logic to calculate lifetime Return On Investment (ROI) and Maximum Drawdown percentages in the Loki mock DB.
24. **Closing-Line EV Tracking:** Build a model drift detector that compares Loki's simulated expected value against the final mock closing odds to score calibration accuracy.
25. **Bankruptcy Probability:** Add a Monte Carlo simulation function estimating the chance of hitting $0 based on the current fractional Kelly staking patterns and variance.
