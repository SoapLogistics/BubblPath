# Architecture Decision Record (ADR) 002: Phase 3B Cognitive Learning Loop

## Status
Approved

## Context
Solomon requires an active, self-improving memory architecture that can parse and retrieve historical tasks, failures, and repairs. However, allowing an AI model to silently write or modify its own operating guidelines (Procedure Cards/Checklists) on disk poses severe self-corruption, loop injection, and security risks.

Additionally, deploying vector databases and dense embedding retrievals in highly sandboxed environments often introduces dependency bloat and strict API key requirements that break offline testability and cost boundaries.

## Decisions
1. **Decoupled Proposal Engine:** We decided that procedures must never be mutated directly. Instead, verified repair operations generate a `PROPOSAL` card. Checklists on disk are only modified when an authorized operator or SS3 review gate promotes the proposal card to `APPROVED` or `ACTIVE`.
2. **Offline Hashing Trick Fallback:** To support semantic hybrid search without active API credentials, we implemented a deterministic, 128-dimensional Feature Hashing Vectorizer (Hashing Trick) in pure Python as a fallback when `OPENAI_API_KEY` is not present. This guarantees full offline testability and runtime availability.
3. **Directed Semantic Graph Links:** Rather than a simple, flat key-value database, relationships between card assets are explicitly tracked via directed labeled link records (`DEPENDS_ON`, `PREVENTS`, `ENHANCES`, `PROPOSES_UPDATE_TO`) to support semantic topological traversal and subgraph query retrieval.
4. **Autonomous Reinforcement Decays:** To handle stale or misleading memories, confidence scores are automatically updated via incremental rewards (`+0.05` on task success) or decays (`-0.10` on task failure). Cards whose confidence falls below `0.30` are automatically demoted to `DRAFT` status and excluded from active retrieval parameters.

## Consequences
- **Pros:**
  - Complete security protection against silent self-corruption or malicious prompt-injection loops.
  - Zero external dependency bloat and 100% reliable test suite execution.
  - Evolving procedural guidelines that grow stronger as workers succeed or fail.
- **Cons:**
  - Slightly more complex model transitions requiring explicit status checks in retrieval queries.
