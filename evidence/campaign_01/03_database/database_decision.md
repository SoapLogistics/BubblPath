# Canonical State Store Decision ADR-007

**Decision Date:** July 27, 2026
**Status:** APPROVED

## Context

Solomon state was fragmented across multiple disconnected database files (`memory_atoms.db`, `solomon_soss.db`), raw binary files (`governance_log.bin`, `solomon_brain_map.bin`), and text logs (`fact_memory.log`). Tests regularly mutated root production files, leading to duplicate empty lesson rows and unstable state tracking.

## Decision

1. **Relational Authority (`solomon_soss.db`):**
   - Unified relational authority inside a single database file `solomon_soss.db` (or custom path passed through constructors).
   - This database manages the schema migrations sequentially up to version 3.
2. **Database Connection Factory Parameters:**
   - Enforce SQLite connections configuring:
     - `PRAGMA foreign_keys = ON;`
     - `PRAGMA journal_mode = WAL;`
     - `PRAGMA busy_timeout = 10000;`
3. **Legacy Disposition:**
   - Deprecate `memory_atoms.db` from production use. It is retained solely as a transient/isolated test state fixture.
   - Restored original, unpolluted root files, completely stopping state contamination.
