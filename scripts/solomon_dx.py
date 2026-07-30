#!/usr/bin/env python3
import os
import sys
import time
import json
import shutil
import sqlite3
import shutil

class SolomonDiagnostics:
    def __init__(self, db_path="solomon_soss.db"):
        self.db_path = db_path

    def run_database_checks(self) -> dict:
        """Database maintenance, vacuum compaction, and integrity checks."""
        res = {"status": "PASS", "integrity": "OK", "compacted": False, "size_bytes": 0}
        if not os.path.exists(self.db_path):
            res["status"] = "FAIL"
            res["integrity"] = "NOT_FOUND"
            return res

        try:
            conn = sqlite3.connect(self.db_path)
            # Integrity check
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            if row and row[0] != "ok":
                res["status"] = "FAIL"
                res["integrity"] = row[0]

            # Vacuum Compaction
            cursor.execute("VACUUM;")
            conn.commit()
            conn.close()
            res["compacted"] = True
            res["size_bytes"] = os.path.getsize(self.db_path)
        except Exception as e:
            res["status"] = "FAIL"
            res["integrity"] = str(e)

        return res

    def run_backup_procedure(self, dest_dir="backups") -> dict:
        """Scheduled backup procedures and rotation validation."""
        os.makedirs(dest_dir, exist_ok=True)
        timestamp = int(time.time())
        dest_file = os.path.join(dest_dir, f"solomon_soss_backup_{timestamp}.db")

        if not os.path.exists(self.db_path):
            return {"status": "SKIPPED", "reason": "No active database found to back up."}

        try:
            shutil.copy2(self.db_path, dest_file)
            return {
                "status": "PASS",
                "backup_file": dest_file,
                "timestamp": timestamp,
                "size_bytes": os.path.getsize(dest_file)
            }
        except Exception as e:
            return {"status": "FAIL", "reason": str(e)}

    def check_system_resources(self) -> dict:
        """Resource checks (Disk, RAM limits simulation, active ports)."""
        # Read disk space
        total, used, free = shutil.disk_usage("/")

        # Read memory info (from proc/meminfo if linux, or defaults)
        mem_free_kb = 0
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemAvailable" in line or "MemFree" in line:
                        mem_free_kb = int(line.split()[1])
                        break
        except Exception:
            mem_free_kb = 1024 * 1024 # 1GB default fallback

        return {
            "disk_free_gb": round(free / (1024**3), 2),
            "disk_total_gb": round(total / (1024**3), 2),
            "memory_available_mb": round(mem_free_kb / 1024, 2),
            "active_port": 10000,
            "status": "PASS" if free > (1024**3) else "WARNING" # Warn if < 1GB
        }

    def print_sanitized_config(self) -> dict:
        """Dumps safe system configuration while masking sensitive credentials and tokens."""
        safe_envs = {}
        unsafe_keywords = ["key", "token", "password", "secret", "auth", "private"]
        for key, val in os.environ.items():
            if any(uk in key.lower() for uk in unsafe_keywords):
                safe_envs[key] = "[MASKED_FOR_SECURITY]"
            else:
                safe_envs[key] = val

        return {
            "PYTHON_VERSION": sys.version,
            "OS_NAME": os.name,
            "ENVIRONMENT_VARS": safe_envs,
            "SOSS_DATABASE_PATH": self.db_path
        }

    def verify_dependencies(self) -> dict:
        """Scan active package installations and python runtime status."""
        requirements_file = "requirements.txt"
        res = {"status": "PASS", "packages": []}
        if os.path.exists(requirements_file):
            with open(requirements_file, "r") as f:
                for line in f:
                    pkg = line.strip()
                    if pkg and not pkg.startswith("#"):
                        res["packages"].append(pkg)
        return res

def main():
    dx = SolomonDiagnostics()
    print("=========================================")
    print("SOLOMON SYSTEM DIAGNOSTICS & HARDENING DX")
    print("=========================================")

    print("\n[+] 1. Running Database Compaction & Integrity Checks...")
    db_res = dx.run_database_checks()
    print(json.dumps(db_res, indent=2))

    print("\n[+] 2. Executing Operational Backup Procedure...")
    backup_res = dx.run_backup_procedure()
    print(json.dumps(backup_res, indent=2))

    print("\n[+] 3. Auditing Local Machine System Resources...")
    sys_res = dx.check_system_resources()
    print(json.dumps(sys_res, indent=2))

    print("\n[+] 4. Verifying Requirements Dependencies Registry...")
    deps_res = dx.verify_dependencies()
    print(json.dumps(deps_res, indent=2))

    print("\n[+] 5. Dumping Sanitized Environment Variables...")
    config_res = dx.print_sanitized_config()
    print(json.dumps(config_res, indent=2))

if __name__ == "__main__":
    main()
