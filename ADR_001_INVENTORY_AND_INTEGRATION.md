# ARCHITECTURAL DECISION RECORD (ADR)
**ADR-001: Consolidated Integration of Mnemosyne and Prometheus Engines**

## Context
Solomon's architecture originally drifted into separate branch paths: one for documentation audits and procedural checklists (Prometheus), and another for the complete executable memory-card storage and retrieval service (Mnemosyne). This division created a split system where the executable code could not read the procedural checklists, and the checklist environment lacked the executable card database.

## Decision
We decided to:
1. Merge the executable Mnemosyne database engine, SQLite database file (`solomon_mnemosyne.db`), and comprehensive unit test suite directly into our active integration branch.
2. Merge the Prometheus capability growth engine and its respective tests alongside Mnemosyne.
3. Perform a startup-level bootstrap integration where `app.py` automatically initializes and imports any missing procedural checklists from `openclaw-workspace/checklists/` on server spin-up via `DoctrineImporter`.
4. Standardize on high-performance SQLite FTS5-based ranked text search over vector embeddings for reliable, low-resource deployment on the Render runtime container.

## Consequences
- **Positive:** Both engines are now co-located on a single branch, allowing the Flask runtime to actively perform pre-task memory recall and post-task draft extraction.
- **Positive:** System state, knowledge cards, and procedural checklists can now be tested, audited, and maintained as a unified whole.
- **Positive:** Zero external dependencies are added to support retrieval, ensuring high reliability and offline execution capability.
- **Neutral:** A small initialization overhead occurs on Flask application startup to scan and import new checklists, but this is mitigated by checking if file paths are already registered.
