# Project Solomon: 50-Step Grand Architecture Optimization

This document outlines 50 intense optimizations spanning the entire Solomon AI framework to enforce hyper-scale performance, memory safety, and cognitive accuracy.

### Category 1: Database & Storage Hyper-Scaling (1-10)
1. **FTS5 Integration:** Add SQLite FTS5 (Full Text Search) virtual tables for massive performance gains in hybrid keyword lookups over `LIKE` or python string overlaps.
2. **PRAGMA Tuning:** Implement `PRAGMA cache_size=-64000`, `PRAGMA temp_store=MEMORY`, and `PRAGMA mmap_size` to push SQLite performance.
3. **Connection Pooling:** Wrap `sqlite3.connect` calls in a thread-safe connection pool or explicitly use `check_same_thread=False` with `threading.local`.
4. **Batched Upserts:** Add `upsert_cards_batch` to `SolomonMnemosyneDB` to process arrays of cards in a single `executemany` transaction.
5. **JSONB Pre-processing:** Store embeddings as serialized blobs or leverage SQLite JSON1 extensions for faster vector parsing.
6. **Card Tombstoning:** Implement soft-deletes (`is_deleted` flag) rather than hard `DELETE` to preserve edge metadata in graph analysis.
7. **Read-Only Replica:** Set up a `file:db.sqlite?mode=ro` URI connection for read-heavy operations like semantic search.
8. **Asynchronous WAL Checkpointing:** Offload `PRAGMA wal_checkpoint` to a background thread to prevent UI freezing during write-heavy bursts.
9. **Index Consolidation:** Implement composite covering indices `(family, confidence)` and `(focus, confidence)`.
10. **Schema Versioning:** Add a `schema_migrations` table to formalize DB structure evolution.

### Category 2: Embeddings & Vector Search (11-20)
11. **Vector Dimension Clipping:** Truncate fallback hashes at exact bit lengths rather than float normalization.
12. **Numpy Fallback:** If `numpy` is installed, route dot products and norms through C-compiled vector math instead of Python comprehensions.
13. **Cosine Similarity Caching:** Cache the exact L2 norm of the `query` during semantic search so it isn't recalculated per card.
14. **Exact Match Short-Circuit:** If `cosine_similarity == 1.0`, immediately halt the search loop and return the definitive match.
15. **Pre-Normalized Vectors:** Store unit-length normalized vectors in DB so cosine similarity becomes a simple dot product, dropping the division and square roots.
16. **Stopword Filtering:** Strip basic stopwords (the, and, is) from the deterministic hash fallback engine to improve entropy.
17. **Batched Async Worker:** Upgrade `AsyncEmbeddingWorker` to use `embed_texts` on chunks of 50 texts at once instead of individual processing.
18. **Low-Confidence Eviction:** Add logic to drop vectors if their confidence score falls below 0.1 for more than 30 days.
19. **Dimensionality Match Guard:** Log warnings when `preferred_embedding` dimensions mismatch the current active model.
20. **Sparse Vector Support Prep:** Add an `is_dense` boolean to the `card_embeddings` schema to prep for SPLADE sparse vectors.

### Category 3: Context Budgeting & Memory (21-30)
21. **Precise Token Counting:** Implement an approximation of `tiktoken` byte-pair encoding (e.g., length / 3.5) for more accurate budgeting than naive length / 4.
22. **Sliding Window Truncation:** Instead of dropping a massive card entirely if it exceeds budget, chunk it on the fly and take the top segment.
23. **Recency Bias Modifier:** Add a timestamp to cards and boost the semantic score of cards created/updated in the last 24 hours.
24. **Semantic Redundancy Penalty (MMR):** Implement Maximal Marginal Relevance. If a retrieved card is >0.90 similar to an already retrieved card, penalize its inclusion to maximize context diversity.
25. **Dynamic Safety Margins:** Increase `safety_margin` exponentially as `task_input_size` grows to buffer against complex reasoning outputs.
26. **Role-Based Prompts:** Structure retrieved context into explicit system roles (`[GOVERNANCE]`, `[HISTORY]`) rather than flat text blocks.
27. **Token Context Export:** Return the total calculated token consumption alongside the context for frontend telemetry rendering.
28. **Budget Exhaustion Logging:** Log a warning to telemetry if the context planner hits 100% budget utilization.
29. **Tiered Relevance Floors:** Set `relevance_threshold` to 0.7 for "Optional" cards but 0.4 for "Failures" to prioritize learning from mistakes.
30. **Memory Card Summarization Prep:** Add a `summary` column to schema to fetch 50-token summaries instead of 2000-token contents when budgets are tight.

### Category 4: Graph Topology & Logic (31-40)
31. **Tarjan's Algorithm:** Replace basic recursion stack cycle detection with Tarjan's Strongly Connected Components algorithm for O(V+E) rigorous cycle mapping.
32. **PageRank Scoring:** Implement a lightweight iterative PageRank score on cards to determine overarching systemic importance during tie-breaks.
33. **Adjacency List Materialization:** Cache the graph as an in-memory dictionary adjacency list rather than hitting SQLite for every `dfs` node link.
34. **Bidirectional Traversal:** Support inverse querying (e.g., "What cards DEPEND_ON this card?") dynamically.
35. **Graph Caching:** Cache the resolved DAG (Directed Acyclic Graph) sequence until a write operation invalidates the graph.
36. **Edge Weights:** Add a `weight` float to `card_links` to differentiate between hard requirements (1.0) and soft suggestions (0.2).
37. **Transitive Reduction:** Build a cleaner script that removes redundant edges (if A->B and B->C, explicitly removing A->C if it was added manually).
38. **Orphan Node Detection:** Identify cards with 0 incoming and 0 outgoing edges for periodic cleanup/review.
39. **Path Length Bounding:** Prevent resolution chains longer than 50 hops to avoid execution pipeline timeouts.
40. **Resolution Explainability Tree:** Format the `explanations` output into a nested JSON tree rather than a flat string array.

### Category 5: System, Flask & Telemetry (41-50)
41. **Gzip Compression:** Wrap Flask responses in Gzip to drastically reduce network latency on massive graph JSON payloads.
42. **Circuit Breaker:** Add a retry/backoff mechanism around the `openai.ChatCompletion` call in `app.py` to handle 429 Rate Limits.
43. **Graceful Shutdown:** Capture SIGTERM and explicitly call `worker.stop()` and `conn.close()` to prevent SQLite corruption on Docker restarts.
44. **Structured JSON Logging:** Convert print statements to `logging.getLogger` with structured JSON formatting for SIEM ingestion.
45. **Process Memory Profiling:** Use `resource.getrusage` in `/health` to report exact RAM usage instead of mock values.
46. **Route Timers:** Add `@app.before_request` and `@app.after_request` to calculate exact MS latency per route for telemetry.
47. **Payload Size Limits:** Enforce Flask `MAX_CONTENT_LENGTH` to prevent OOM DOS attacks on the ingestion endpoints.
48. **CORS Hardening:** Restrict Cross-Origin Resource Sharing exclusively to the Chrome Extension UUID or localhost ports.
49. **Loki Background Thread:** Shift Loki Simulation heavy Monte Carlo math to a background thread and return Job IDs to prevent request timeouts.
50. **System Status File Lock:** Write a `/tmp/solomon.lock` containing the active PID to ensure only one instance binds to the local SQLite WAL simultaneously.
