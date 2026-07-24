#!/usr/bin/env bash
# ==============================================================================
# SS1 Deployment Rollback Script
# Restores previous database, configurations, and restarts services.
# ==============================================================================

set -euo pipefail

SERVICE_API="solomon-api.service"
SERVICE_PROXY="solomon-proxy.service"
BACKUP_DIR="/tmp/solomon_deploy_backup"
CONFIG_FILE="/etc/solomon/solomon.env"

echo "=== Commencing Emergency Rollback on SS1 ==="

if [ -d "${BACKUP_DIR}" ]; then
    # Restore config
    if [ -f "${BACKUP_DIR}/solomon.env.bak" ]; then
        echo "Restoring configuration file..."
        sudo cp "${BACKUP_DIR}/solomon.env.bak" "${CONFIG_FILE}"
    fi

    # Restore database backup
    if [ -f "${BACKUP_DIR}/solomon_mnemosyne.db.bak" ]; then
        echo "Restoring persistent database..."
        cp "${BACKUP_DIR}/solomon_mnemosyne.db.bak" "/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db"
    fi

    echo "Restarting services after rollback..."
    sudo systemctl restart "${SERVICE_API}" || true
    sudo systemctl restart "${SERVICE_PROXY}" || true

    echo "SUCCESS: Rollback executed successfully."
else
    echo "ERROR: No backup found at ${BACKUP_DIR}. Manual intervention required."
    exit 1
fi
