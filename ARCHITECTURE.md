# Project Mnemosyne: Knowledge Card Engine Architecture

This document specifies the architecture of **Project Mnemosyne**, Solomon's production-grade, long-term memory and cognitive feedback subsystem (Phase 3A).

---

## 1. System Topology & Layers

The engine is built as a highly decoupled, modular Python package (`solomon_knowledge_cards`) integrated directly with the SQLite database layer. It is designed to bridge ephemeral worker runtime states with governed, long-term operational guidelines.

```
                  ┌─────────────────────────────────────┐
                  │           Worker Report             │
                  │   (Task Outputs & Ingested Events)  │
                  └──────────────────┬──────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │       KnowledgeExtractor            │
                  │ (Extracts draft cards from context) │
                  └──────────────────┬──────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │             ReviewGate              │
                  │ (Transition gate: DRAFT -> ACTIVE)  │
                  └──────────────────┬──────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │          DatabaseManager            │
                  │  (Thread-safe SQLite storage API)  │
                  └─────────────────────────────────────┘
```

---

## 2. Component Design & Responsibilities

### A. Canonical Card Model (`models/card.py`)
Provides schema enforcement and field validation for all memory cards.
- **Required Fields:** ID, Type, Schema Version, Title, Summary, Body, Status, Confidence, Validation State, Created At, Updated At, Created By, Source Type, Evidence, Security Classification.
- **Why Does This Exist? Fields:**
  - `why_created`: Core rationale of why the memory was codified.
  - `problem_solved`: Precise description of what issue/error/constraint is resolved.
  - `future_work_dependent`: Predicts future capabilities or worker routines reliant on this memory.
- **Supported Enums:**
  - *Types:* `KNOWLEDGE`, `LESSON`, `FAILURE`, `REPAIR`, `DECISION`, `SKILL`
  - *Statuses:* `DRAFT`, `REVIEWED`, `APPROVED`, `ACTIVE`, `DEPRECATED`
  - *Validation States:* `UNVALIDATED`, `VALID`, `INVALID`

### B. Storage Layer (`storage/db.py`)
Handles connection pool initialization, schema migrations, and atomic writes.
- **Atomic Operations:** Uses transaction boundaries for inserting/updating cards and rewriting links/tags.
- **Concurrency & Thread Safety:** Implements reentrant locks (`RLock`) and custom `busy_timeout` PRAGMAs to guarantee thread-safe writes in asynchronous runtime schedules.
- **Revision History:** Every write triggers a complete record insertion into `card_revisions` mapping full serialized card states, reasons, timestamps, and authors.
- **Soft Deletion:** Deprecating or deleting a card updates `deleted = 1` and `status = 'DEPRECATED'` while preserving history.
- **Backup & Recovery:** Supports exporting/importing system states via high-performance JSONL files.

### C. Repository API (`api/repository.py`)
Offers clean, tested service methods for CRUD operations, card linking, and list retrieval.
- **Ranked Search Algorithm:** Computes relevance scores based on query terms matching weighted fields:
  - `Title`: 10.0 pts
  - `Tags`: 8.0 pts
  - `Rationale Fields (Why/Problem)`: 6.0 pts
  - `Summary`: 5.0 pts
  - `Body`: 2.0 pts
- **Search Explanation:** Provides an analytical string explaining why a memory was selected, factoring in card confidence scores as multipliers.

### D. Knowledge Extraction Pipeline (`extractor/extractor.py`)
A deterministic parsing pipeline that turns Worker Reports and SS3 Review results into candidate draft cards.
- Detects partial failures, complete failures, and successful hotfixes.
- Evaluates outcome details, maps root causes, and assigns parent/child/related linking constraints.

### E. Review Gate (`api/review.py`)
Enforces the formal state transition sequence:
- `DRAFT` ➔ `REVIEWED` ➔ `APPROVED` ➔ `ACTIVE`.
- Unapproved card states are never served as trusted guidance. Rejected cards are flagged as `DEPRECATED` with transition notes preserved.

---

## 3. Storage Schema Mapping

### Table: `cards`
- `card_id` TEXT PRIMARY KEY
- `card_type` TEXT NOT NULL
- `schema_version` TEXT NOT NULL
- `title` TEXT NOT NULL
- `summary` TEXT NOT NULL
- `body` TEXT NOT NULL
- `status` TEXT NOT NULL
- `confidence` REAL NOT NULL
- `validation_state` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL
- `created_by` TEXT NOT NULL
- `source_type` TEXT NOT NULL
- `security_classification` TEXT NOT NULL
- `evidence` TEXT NOT NULL
- `supersedes` TEXT
- `superseded_by` TEXT
- `why_created` TEXT NOT NULL
- `problem_solved` TEXT NOT NULL
- `future_work_dependent` TEXT NOT NULL
- `extra_metadata` TEXT (JSON serialized)
- `deleted` INTEGER DEFAULT 0

### Table: `card_revisions`
- `revision_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `card_id` TEXT NOT NULL
- `revision_number` INTEGER NOT NULL
- `serialized_card` TEXT NOT NULL
- `updated_at` TEXT NOT NULL
- `updated_by` TEXT NOT NULL
- `reason` TEXT

### Table: `card_links`
- `link_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `source_id` TEXT NOT NULL
- `target_id` TEXT NOT NULL
- `link_type` TEXT NOT NULL (e.g., 'PARENT', 'RELATED')
- UNIQUE (`source_id`, `target_id`, `link_type`)
