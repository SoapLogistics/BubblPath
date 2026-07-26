#!/bin/bash
export PYTHONPATH=.
python3 tests/integration/soss_workspace_comms_smoke.py
python3 tests/integration/test_service_smokes.py
python3 tests/test_joe_refusal.py
python3 tests/test_service_registry.py
echo "All checks passed."
