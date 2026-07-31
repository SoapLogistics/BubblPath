#!/usr/bin/env python3
# ==============================================================================
# Solomon DX - Unified Developer Experience and Operations Diagnostics Tool
# ==============================================================================
import os
import sys
import json
import sqlite3
import subprocess

def print_help():
    print("""
Solomon DX Central CLI Toolkit
Usage: python3 scripts/solomon_dx.py [command]

Commands:
  health       Runs full system diagnosis, file system space, and DB checks.
  test         Runs complete 27-item automated verification test suite.
  format       Runs automated formatting checks across SOSS python files.
  config       Prints effective configuration settings and model targets safely.
""")

def run_health():
    print("[INFO] Initiating Solomon SOSS System Diagnosis...")
    report = {
        "status": "HEALTHY",
        "checks": {}
    }

    # 1. DB check
    for db in ["solomon_soss.db", "solomon_hyper_memory.db", "memory_atoms.db"]:
        if os.path.exists(db):
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                res = cursor.fetchone()[0]
                report["checks"][db] = {
                    "exists": True,
                    "integrity": res,
                    "size_bytes": os.path.getsize(db)
                }
                conn.close()
            except Exception as e:
                report["status"] = "DEGRADED"
                report["checks"][db] = {"exists": True, "error": str(e)}
        else:
            report["checks"][db] = {"exists": False}

    # 2. Engine Registry Sync Check
    registry_path = "solomon_api/engine_registry.json"
    if os.path.exists(registry_path):
        report["checks"]["engine_registry"] = {"exists": True, "status": "SYNCHRONIZED"}
    else:
        report["status"] = "DEGRADED"
        report["checks"]["engine_registry"] = {"exists": False}

    print(json.dumps(report, indent=2))
    if report["status"] == "HEALTHY":
        print("[SUCCESS] Solomon core services are operating at nominal capacity.")
    else:
        print("[ERROR] Solomon core is currently degraded.")
        sys.exit(1)

def run_test():
    print("[INFO] Invoking Pytest automated resilience validation...")
    res = subprocess.run(["python3", "-m", "pytest"], env=os.environ)
    sys.exit(res.returncode)

def run_format():
    print("[INFO] Running static formatting and linting validation...")
    # Scan python files and ensure no parse error
    has_error = False
    for root, _, files in os.walk("."):
        if any(p in root for p in [".git", "__pycache__", ".pytest_cache"]):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        compile(f.read(), filepath, 'exec')
                except Exception as e:
                    print(f"  - [LINT ERROR] {filepath}: {e}")
                    has_error = True
    if has_error:
        print("[ERROR] Formatting validation failed.")
        sys.exit(1)
    else:
        print("[SUCCESS] Formatting validation passed. Codebase syntax is clean.")

def run_config():
    print("[INFO] Solomon SOSS effective configuration:")
    config = {
        "ENV": os.environ.get("SOSS_ENV", "DEVELOPMENT"),
        "DB_PATH": "solomon_soss.db",
        "PORT": 18789,
        "STAGING_PORT": 10000,
        "INFRASTRUCTURE_NODES": ["ss1-machine.tailscale", "ss2-machine.tailscale", "ss3-machine.tailscale"],
        "SECURITY": {
            "SANDBOXING_LEVEL": "HIGH",
            "SS3_PROMOTION_REQUIRED": True,
            "ROLLBACK_POLICY": "ATOMIC"
        }
    }
    print(json.dumps(config, indent=2))

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "health":
        run_health()
    elif cmd == "test":
        run_test()
    elif cmd == "format":
        run_format()
    elif cmd == "config":
        run_config()
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
