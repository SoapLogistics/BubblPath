#!/usr/bin/env bash
# ==============================================================================
# SOSS Developer Pre-Commit Hook Integration
# ==============================================================================
set -euo pipefail

echo "[PRE-COMMIT] Validating codebase formatting and syntax..."
python3 scripts/solomon_dx.py format

echo "[PRE-COMMIT] Running full automated verification suite..."
python3 scripts/solomon_dx.py test

echo "[PRE-COMMIT] Validation passed. Ready to commit!"
