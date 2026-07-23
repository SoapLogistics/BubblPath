"""
Solomon Perpetual Learning Machine
Phase 15: Proactive Self-Repair and Adaptive Patching

This module implements:
1. Automated file corruption recovery using cached backup templates.
2. Dynamic parameter adjustments on runtime metric warnings.
"""

import os
import shutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AdaptivePatchingEngine:
    """
    Autonomously tracks capability file health and triggers automated
    patches and file restores on file mutations or syntax corruptions.
    """

    def __init__(self, backup_dir: str = "backup_capabilities"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_file(self, filepath: str) -> bool:
        """
        Caches a stable file backup template inside the backup repository.
        """
        if not os.path.exists(filepath):
            return False
        try:
            shutil.copy2(filepath, os.path.join(self.backup_dir, os.path.basename(filepath)))
            return True
        except Exception as e:
            logger.error(f"Backup failed for {filepath}: {str(e)}")
            return False

    def verify_and_patch_file(self, filepath: str) -> Dict[str, Any]:
        """
        Audits file compile syntax. On failure, restores file from cache and logs active patch.
        """
        if not os.path.exists(filepath):
            return {"success": False, "status": "FILE_MISSING"}

        # 1. Compile Check
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, filepath, "exec")
            return {"success": True, "status": "HEALTHY"}
        except (SyntaxError, Exception) as se:
            # 2. Re-compile failed! Restore from backup
            backup_file = os.path.join(self.backup_dir, os.path.basename(filepath))
            if os.path.exists(backup_file):
                try:
                    shutil.copy2(backup_file, filepath)
                    return {
                        "success": True,
                        "status": "PATCHED_AND_RESTORED",
                        "error_remedied": str(se),
                        "message": f"Successfully patched and restored corrupted file {filepath} from stable cache."
                    }
                except Exception as re:
                    return {
                        "success": False,
                        "status": "RESTORE_FAILED",
                        "error": str(re)
                    }
            return {
                "success": False,
                "status": "CORRUPTED_NO_BACKUP",
                "error": str(se)
            }
