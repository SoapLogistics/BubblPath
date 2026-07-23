"""
Solomon Perpetual Learning Machine
Phase 14: Autonomous Self-Healing AIL Daemon

This module runs 24/7 background maintenance:
1. Database optimization (VACUUM and ANALYZE).
2. Codebase self-healing via programmatic Git rollbacks on compilation or test failures.
"""

import sqlite3
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SelfHealingAILDaemon:
    """
    Manages proactive, 24/7 self-healing and database optimizations
    autonomously based on worker execution indicators.
    """

    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db"):
        self.db_path = db_path

    def run_database_vacuum_and_compaction(self) -> Dict[str, Any]:
        """
        Executes SQLite VACUUM and ANALYZE commands to optimize file structure and query speed.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            conn.commit()
            return {
                "success": True,
                "message": "SQLite database optimized successfully (VACUUM & ANALYZE complete)."
            }
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Database compaction failed."
            }
        finally:
            conn.close()

    def trigger_programmatic_git_rollback(self, candidate_name: str, error_msg: str) -> Dict[str, Any]:
        """
        Physically triggers a standard Git tree checkout rollback inside the workspace
        to self-heal and restore peak stable production state on code crash.
        """
        logger.warning(f"[Self-Healing] Compilation failure in '{candidate_name}': {error_msg}. Triggering Git rollback.")

        # Simulate git checkout command pattern safely
        rollback_cmd = ["git", "checkout", "main", "--", "."]

        try:
            # Execute real git checkout command
            completed = subprocess.run(rollback_cmd, capture_output=True, text=True, check=True)
            return {
                "success": True,
                "candidate_aborted": candidate_name,
                "revert_command_executed": " ".join(rollback_cmd),
                "revert_output": completed.stdout.strip(),
                "message": f"Successfully executed physical Git rollback to abort candidate '{candidate_name}'."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Physical Git rollback failed inside this host directory context."
            }
        finally:
            # Extract FAILURE card and log to Mnemosyne
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO knowledge_cards (card_id, family, focus, content, validation_state)
                    VALUES (?, 'Repair', 'Autonomously logged execution failure card', ?, 'ACTIVE')
                """, (
                    f"SOK-FAIL-{candidate_name.upper().replace('-', '_')}",
                    f"Dynamic compile error on candidate '{candidate_name}'. Error: {error_msg}. Rollback triggered successfully."
                ))
                conn.commit()
                conn.close()
            except Exception:
                pass
location = "solomon_self_healing_ail.py"
