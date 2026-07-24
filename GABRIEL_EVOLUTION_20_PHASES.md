# GABRIEL OS KERNEL: 20-PHASE EVOLUTION PLAN

This document outlines 20 immediate architectural and algorithmic improvements to build upon the newly converged Solomon/Gabriel OS Kernel. These phases transition the scaffolding into robust, production-ready capabilities.

## Core Worker & Graph Enhancements (Phases 1-5)
1. **Worker Success Tracking:** Augment `GabrielKernel` to track historical success/failure rates for each worker to influence routing decisions dynamically.
2. **Semantic Context Summarization:** Upgrade `DynamicContextEngine` to not just truncate context, but recursively summarize older context blocks using an internal LLM worker when VRAM is tight.
3. **Context Deduplication:** Add similarity-based deduplication to context arrays to remove redundant semantic information before LLM inference.
4. **Subgraph BFS Querying:** Expand `UniversalKnowledgeGraph` with breadth-first search (BFS) capability to pull localized context spheres (N-degree neighbors) instead of just isolated nodes.
5. **Node Expiration (TTL Pruning):** Implement Time-To-Live logic on graph nodes to automatically prune stale runtime data, preventing unbounded memory bloat.

## Routing, Telemetry & Learning Enhancements (Phases 6-10)
6. **Consensus Worker Routing:** If a task complexity is exceedingly high, route the task to multiple workers and implement a consensus-voting mechanism before returning the result.
7. **Fallback Worker Chains:** Implement automatic retry routing—if a preferred worker (e.g., local 4-bit) fails, fallback to a heavier worker (e.g., OpenAI API) dynamically.
8. **Financial & Energy Telemetry:** Upgrade `UnifiedDashboard` to track and report estimated USD API costs and KW/h energy consumption based on hardware profiling.
9. **Background Skill Benchmarking:** Upgrade `SkillAssimilation` to periodically benchmark extracted skills against a validation set, assigning a confidence score to each generated tool.
10. **Automated Research Hypotheses:** Connect `CuriosityEngine` failures directly into a prompt generator that proposes a "Research Hypothesis" graph node.

## Predictive Metrics & Storage (Phases 11-15)
11. **Predictive Task Complexity:** Add a pre-routing analytical step in `SolomonOSKernel` that scores incoming task complexity based on token length and verb extraction.
12. **Cold Memory Disk Swapping:** Implement tiered context arrays where older context is offloaded to a local `.bin` file and swapped back into RAM only when semantically triggered.
13. **Quantization Precision Penalties:** Add logic to `QuantizationCore` to calculate confidence penalties when executing tasks under high quantization (e.g., INT4).
14. **Cross-Worker Memory Sharing:** Ensure that `ContinuousLearningPipeline` broadcasts learned skills across all registered workers, not just the one that solved the problem.
15. **Dashboard Latency Profiling:** Add precise sub-millisecond latency tracking across the 3 main pipeline steps (Budget, Route, Learning Ingestion).

## API Exposure & System Integrations (Phases 16-20)
16. **Gabriel Health API:** Expose `/api/gabriel/health` on Flask to output the full UnifiedDashboard metrics in real-time.
17. **Graph Visualization API:** Expose `/api/gabriel/graph` to return the Knowledge Graph edge list for frontend D3.js visualization.
18. **Skill Registry API:** Expose `/api/gabriel/skills` to retrieve indexed, benchmarked skills.
19. **Curiosity Queue API:** Expose `/api/gabriel/curiosity` to expose the autonomous research backlog.
20. **Dynamic Optimization Override Endpoint:** Expose `/api/gabriel/optimize` to allow users to manually trigger the `RecursiveOptimizer` logic outside the standard chat loop.
