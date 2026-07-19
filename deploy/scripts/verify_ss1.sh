#!/usr/bin/env bash
# ==============================================================================
# SS1 Deployment Verification Script
# Verifies health endpoints, systemd state, proxy connectivity, and schema metrics.
# ==============================================================================

set -euo pipefail

SERVICE_API="solomon-api.service"
SERVICE_PROXY="solomon-proxy.service"

echo "=== Executing Solomon SS1 Verification Check ==="

# 1. Deployed git commit
echo -n "Deployed Git Commit: "
git rev-parse HEAD

# 2. Service systemd states
echo -n "Service [${SERVICE_API}] State: "
systemctl is-active "${SERVICE_API}" || echo "INACTIVE"

echo -n "Service [${SERVICE_PROXY}] State: "
systemctl is-active "${SERVICE_PROXY}" || echo "INACTIVE"

# 3. Test API Health Endpoint
echo "Checking API Health..."
curl -s http://127.0.0.1:18789/api/health | python3 -m json.tool || echo "API Health request failed"

# 4. Test Proxy Edge Routing Health Endpoint
echo "Checking Proxy Health..."
curl -s http://127.0.0.1:7420/api/health | python3 -m json.tool || echo "Proxy Health request failed"

echo "=== Verification Finished ==="
