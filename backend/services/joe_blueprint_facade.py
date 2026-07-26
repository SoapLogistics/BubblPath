import json
import subprocess
import os

# Backend facade shouldn't directly import from services/ due to Pattern B.
# It should interact via a safe boundary (e.g., subprocess or separate process) for real execution.
# For dry_run, we can use a safe deterministic heuristic without importing the real engine.

def queue_blueprint(blueprint_text, mode="dry_run"):
    if mode != "dry_run":
        raise Exception("Execution mode not approved.")

    # Deterministic generation for dry run
    return {
        "status": "dry_run",
        "risk": "medium",
        "tests_required": True,
        "files_affected": [],
        "approvals": ["Mark"],
        "next_steps": ["Review packet"]
    }
