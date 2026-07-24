#!/usr/bin/env bash
# ==============================================================================
# SS1 Deployment Script
# Safely deploys the Solomon API & Mnemosyne package, runs migrations/tests,
# and restarts systemd services on SS1. Autodetects Git status and rolls back on failure.
# ==============================================================================

set -euo pipefail

# Configurations
SERVICE_API="solomon-api.service"
SERVICE_PROXY="solomon-proxy.service"
CONFIG_FILE="/etc/solomon/solomon.env"
BACKUP_DIR="/tmp/solomon_deploy_backup"
DEPLOY_DIR="$(pwd)"

echo "=== Starting Solomon SS1 Safe Deployment ==="

# 1. Refuse dirty tree unless overridden
if [ -n "$(git status --porcelain)" ] && [ "${FORCE_DEPLOY:-0}" -ne 1 ]; then
    echo "ERROR: Working tree is dirty. Please commit or stash changes before deploying."
    echo "To override, run: FORCE_DEPLOY=1 ./deploy_ss1.sh"
    exit 1
fi

# 2. Record current deployed commit
DEPLOYED_COMMIT=$(git rev-parse HEAD)
echo "Deploying commit: ${DEPLOYED_COMMIT}"

# 3. Create a backup / rollback point
echo "Creating backup of current state..."
rm -rf "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"
if [ -f "${CONFIG_FILE}" ]; then
    cp "${CONFIG_FILE}" "${BACKUP_DIR}/solomon.env.bak"
fi
# Back up database if exists
if [ -f "/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db" ]; then
    cp "/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db" "${BACKUP_DIR}/solomon_mnemosyne.db.bak"
fi

# 4. Install dependencies deterministically
echo "Installing backend dependencies..."
python3 -m pip install -r requirements.txt --quiet

# 5. Create required directories with safe permissions
echo "Ensuring data directory path exists..."
mkdir -p /srv/storage/toshiba/BubblePath/data/mnemosyne
chmod 750 /srv/storage/toshiba/BubblePath/data/mnemosyne

# 6. Run migrations & database tests
echo "Executing unit tests & validation migrations..."
PYTHONPATH=. python3 -m pytest tests/ || {
    echo "ERROR: Tests or schema validation failed! Aborting deployment."
    exit 1
}

# 7. Restart services safely
echo "Reloading systemd and restarting services..."
if systemctl is-active --quiet "${SERVICE_API}" 2>/dev/null; then
    sudo systemctl restart "${SERVICE_API}"
else
    echo "Warning: Service ${SERVICE_API} not active or not installed. Attempting reload/start..."
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_API}" || true
    sudo systemctl start "${SERVICE_API}" || true
fi

if systemctl is-active --quiet "${SERVICE_PROXY}" 2>/dev/null; then
    sudo systemctl restart "${SERVICE_PROXY}"
else
    echo "Warning: Service ${SERVICE_PROXY} not active or not installed. Attempting reload/start..."
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_PROXY}" || true
    sudo systemctl start "${SERVICE_PROXY}" || true
fi

# 8. Check health and readiness with automatic rollback
echo "Checking service readiness..."
sleep 2

# Exercise readiness endpoint
READINESS_URL="http://127.0.0.1:18789/api/health"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${READINESS_URL}" || echo "000")

if [ "${HTTP_STATUS}" -eq 200 ]; then
    echo "SUCCESS: Readiness endpoint returned 200 OK."
    echo "Deployment of commit ${DEPLOYED_COMMIT} completed successfully!"
else
    echo "ERROR: Readiness endpoint returned status ${HTTP_STATUS}. Initiating automated rollback..."
    ./rollback_ss1.sh
    exit 1
fi
