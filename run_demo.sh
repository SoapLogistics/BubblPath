#!/bin/bash
set -e

echo "Cleaning up any prior demonstration state..."
rm -f solomon_soss.db memory_atoms.db governance_log.bin
rm -rf evidence_artifacts/

echo "Starting Perpetual Learning Cycle Demonstration..."
PYTHONPATH=. python scripts/demonstrate_plc.py

echo ""
echo "Simulating Runtime Restart (checking state retention)..."
PYTHONPATH=. python scripts/demonstrate_plc.py

echo ""
echo "Verification Complete. All evidence generated."
