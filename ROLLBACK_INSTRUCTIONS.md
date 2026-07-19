# Project Mnemosyne: Rollback Instructions

This document provides step-by-step instructions on how to safely rollback or recover the Solomon Knowledge Card database in case of production failures, corruption, or schema regression.

---

## 1. Database Rollback Procedures

### Scenario A: Corruption during Runtime
If the active SQLite database (`solomon_cards.db`) is corrupted or enters a lock contention loop:
1. **Identify the Process:** Identify all active worker processes accessing the DB:
   ```bash
   lsof solomon_cards.db
   ```
2. **Terminate Contenders:** Safely terminate those processes:
   ```bash
   kill -9 <PID>
   ```
3. **Restore from Last Known Good Backup:**
   Remove the corrupted database file and import the last valid JSONL backup file:
   ```python
   from solomon_knowledge_cards.storage.db import DatabaseManager
   import os

   # Remove corrupted DB
   if os.path.exists("solomon_cards.db"):
       os.remove("solomon_cards.db")

   # Initialize and import
   db = DatabaseManager("solomon_cards.db")
   db.import_from_jsonl("backups/last_valid_backup.jsonl")
   ```

### Scenario B: Schema Migration Regression
If a newly applied database schema migration breaks compatibility with existing card structures:
1. **Halt System Cycles:** Terminate the continuous autonomous heartbeat.
2. **Retrieve Schema Version:** Check the current applied migration version:
   ```sqlite3 solomon_cards.db "SELECT MAX(version) FROM schema_version;"
   ```
3. **Downgrade Procedure:**
   SQLite does not support backward migration steps automatically. To revert to Migration `N-1`:
   - Export all active card data to a JSONL backup:
     ```python
     db.export_to_jsonl("temp_migration_backup.jsonl")
     ```
   - Delete the current database file.
   - Revert your repository branch code back to the previous version (this restores the previous `DatabaseManager` schema setup).
   - Reinitialize the database file (which will run the old migrations up to version `N-1`).
   - Import the data back:
     ```python
     db.import_from_jsonl("temp_migration_backup.jsonl")
     ```

## 2. Emergency Backup Commands
To trigger a manual snapshot of the database state:
```bash
python3 -c "
from solomon_knowledge_cards.storage.db import DatabaseManager
db = DatabaseManager('solomon_cards.db')
db.export_to_jsonl('backups/emergency_backup_$(date +%Y%m%d_%H%M%S).jsonl')
print('Emergency backup successful')
"
```
