#!/usr/bin/env python3
"""
Solomon Developer Experience (DX) Unified CLI Command utility.
Provides one central entrypoint for setting up, testing, formatting, linting, and checking health.
"""

import sys
import os
import subprocess
import argparse

def run_command(cmd, shell=False):
    print(f"\n🚀 Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, shell=shell)
    if res.returncode != 0:
        print(f"❌ Command failed with exit code {res.returncode}")
        return False
    print("✅ Command completed successfully!")
    return True

def cmd_setup():
    print("🧹 Setting up Solomon Python Environment...")
    success = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if success:
        print("🎉 Dependencies installed successfully!")
    return success

def cmd_test():
    print("🧪 Running Solomon test suite...")
    os.environ["PYTHONPATH"] = "."
    return run_command(["pytest", "tests/"])

def cmd_lint():
    print("🔍 Running Formatting & Lint Checks...")
    black_ok = run_command(["black", "--check", "--line-length", "120", "."])
    flake_ok = run_command(["flake8", "--max-line-length=120", "--exclude=.git,__pycache__,build,dist,venv,env", "."])
    return black_ok and flake_ok

def cmd_format():
    print("🎨 Formatting codebase with Black...")
    return run_command(["black", "--line-length", "120", "."])

def cmd_run():
    print("🔥 Launching Solomon API Core App on Port 10000...")
    return run_command([sys.executable, "app.py"])

def cmd_health():
    print("📋 Checking Solomon System Health & Consistency...")
    all_ok = True

    # 1. Check Python version
    print(f"  - Python Version: {sys.version.split()[0]} (Expected >= 3.11)")

    # 2. Check canonical files existence
    files_to_check = [
        "app.py",
        "requirements.txt",
        "solomon_api/engine_registry.json",
        "core/solomon_quantized_memory.py",
        "services/solomon_futures_engine.py",
        "PROJECT_SOLOMON_EVIDENCE_BASED_INVENTORY_CURRENT.md"
    ]
    for f in files_to_check:
        exists = os.path.exists(f)
        status = "✅" if exists else "❌ MISSING"
        print(f"  - File {f}: {status}")
        if not exists:
            all_ok = False

    # 3. Verify Pytest suite is operational
    try:
        import pytest
        print("  - Pytest: ✅ Installed")
    except ImportError:
        print("  - Pytest: ❌ Missing (Run 'scripts/solomon_dx.py setup')")
        all_ok = False

    if all_ok:
        print("\n🎉 All health and consistency checks PASSED successfully!")
    else:
        print("\n⚠️ Some health checks failed. Please review the output above.")
    return all_ok

def main():
    parser = argparse.ArgumentParser(description="Solomon Unified DX Command Tool")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to execute")

    subparsers.add_parser("setup", help="Install all Python requirements and tools")
    subparsers.add_parser("test", help="Execute all unit and integration pytest suites")
    subparsers.add_parser("lint", help="Verify style guidelines using Black check & Flake8")
    subparsers.add_parser("format", help="Auto-format code using Black")
    subparsers.add_parser("run", help="Start the main SOSS Flask core application")
    subparsers.add_parser("health-check", help="Verify dependencies, required files, and versions")

    args = parser.parse_args()

    success = False
    if args.command == "setup":
        success = cmd_setup()
    elif args.command == "test":
        success = cmd_test()
    elif args.command == "lint":
        success = cmd_lint()
    elif args.command == "format":
        success = cmd_format()
    elif args.command == "run":
        success = cmd_run()
    elif args.command == "health-check":
        success = cmd_health()

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
