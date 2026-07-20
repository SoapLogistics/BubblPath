# Perpetual Learning Core (PLC) Engine Architecture & Threat Model

## 1. Package Architecture (`solomon_knowledge_cards`)
The Python implementation serves as a structured, transaction-safe, and audited framework mirroring Solomon’s **Perpetual Learning Core (PLC)**:

*   **`models.py`:** Core object definitions (`KnowledgeCardModel`) ensuring schema validation, type integrity checks, rationale fields, and relation definitions.
*   **`db.py`:** Standard SQLite backend configured in Write-Ahead Logging (WAL) high-concurrency mode with support for audit logging via `card_revisions`.
*   **`repository.py`:** Complete CRUD endpoints, directed relation links, and tag indexes.
*   **`engine.py`:** Asynchronous parser for Worker Reports, Review Gates (Draft -> Reviewed -> Approved -> Active), and strictly trusted active retrieval.
*   **`importer.py`:** Safe markdown parser mapping original procedural checklists (e.g., PC-SO-01) into our database structure cleanly.

---

## 2. Threat Model Analysis

| Threat Signature | Risk Level | Mitigation Strategy |
| :--- | :--- | :--- |
| **Direct database manipulation** | High | SQLite WAL mode limits outside file corruption. All operational modifications are logged in transactional history records. |
| **PII/Secrets leak in cards** | Medium | The pipeline sanitizes secrets, keys, and environment variables prior to writing draft records. |
| **Unauthorized auto-mutation of live SOPs** | High | Every generated card begins strictly as a `DRAFT` in `PENDING` state. Only humans/SS3 reviewed items reach active deployment. |
| **Race conditions during concurrent task execution** | Medium | Row locking, automatic retries, and high-performance connection pool configuration prevent deadlocks. |

---

## 3. Rollback & Recovery Procedures
- **Rollback Routine:** A soft delete sets a card status to `ARCHIVED`, ensuring historic traces are not lost.
- **Recovery Setup:** Regular offline scheduled dumps output entire database states to JSONLines (JSONL) records using `export_to_jsonl`. System states can be fully reconstructed via `import_from_jsonl` if database corruption occurs.
