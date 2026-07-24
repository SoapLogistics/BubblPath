#!/usr/bin/env bash
# ==============================================================================
# Solomon Live Verification Tool
# Executable script to verify deployment state, connection, and database metrics.
# Does NOT print sensitive keys or credentials.
# ==============================================================================

set -euo pipefail

API_PORT=18789
PROXY_PORT=7420

echo "=== Solomon SS1 Deployment Status ==="
echo "Deployed Commit: $(git rev-parse HEAD)"

# Systemd checks
echo "Checking Systemd services:"
for svc in "solomon-api" "solomon-proxy"; do
    if systemctl list-units --full --all | grep -Fq "${svc}.service"; then
        echo "  - ${svc}: $(systemctl is-active ${svc}.service)"
    else
        echo "  - ${svc}: NOT INSTALLED"
    fi
done

# DB status
DB_PATH="/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db"
if [ -f "${DB_PATH}" ]; then
    echo "Database: Found at ${DB_PATH}"
else
    echo "Database: Not found at production location. Checking locally..."
    DB_PATH="./solomon_mnemosyne.db"
fi

# Checking local connection and database count via Python helper
python3 -c "
import os, sys
try:
    from solomon_knowledge_cards import MnemosyneRuntime
    runtime = MnemosyneRuntime('${DB_PATH}')
    h = runtime.health()
    print('  - Connected:', h.get('connected'))
    print('  - Schema version:', h.get('schema_version'))
    print('  - Card count:', h.get('card_count'))
except Exception as e:
    print('  - Error fetching database metrics:', str(e))
"

echo "=== Health Endpoint Status ==="
echo "Testing API backend health (port ${API_PORT}):"
curl -s "http://127.0.0.1:${API_PORT}/api/health" || echo "  - Unreachable"

echo "Testing Proxy health (port ${PROXY_PORT}):"
curl -s "http://127.0.0.1:${PROXY_PORT}/api/health" || echo "  - Unreachable"

echo "================================================="
echo "Verification query complete."
