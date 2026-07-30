#!/usr/bin/env bash
# ==============================================================================
# Solomon SOSS Canonical Backup & Recovery Manager
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/solomon}"
DATA_DIR="${DATA_DIR:-/opt/solomon/soss}"
RETENTION_COUNT=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RUN_DIR="${BACKUP_DIR}/run_${TIMESTAMP}"

echo "[INFO] Starting backup of Solomon SOSS at ${TIMESTAMP}..."

# Create backup directories
mkdir -p "${BACKUP_DIR}"
mkdir -p "${RUN_DIR}"

# 1. Back up databases (Using sqlite3 .backup to avoid half-written state corruption)
echo "[INFO] Backing up SOSS databases..."
for db in "solomon_soss.db" "solomon_hyper_memory.db" "memory_atoms.db"; do
    if [ -f "${DATA_DIR}/${db}" ]; then
        sqlite3 "${DATA_DIR}/${db}" ".backup '${RUN_DIR}/${db}'"
        echo "  - Backed up ${db}"
    else
        echo "  - [WARN] ${db} not found, skipping."
    fi
done

# 2. Back up config files and engine registry
echo "[INFO] Backing up system configuration..."
mkdir -p "${RUN_DIR}/config"
if [ -d "${DATA_DIR}/config" ]; then
    cp -r "${DATA_DIR}/config/"* "${RUN_DIR}/config/"
fi
if [ -d "${DATA_DIR}/solomon_api" ]; then
    cp -r "${DATA_DIR}/solomon_api" "${RUN_DIR}/"
fi

# 3. Back up audit and governance logs
echo "[INFO] Backing up audit logs..."
for log in "governance_log.bin" "solomon_integration_audit.md"; do
    if [ -f "${DATA_DIR}/${log}" ]; then
        cp "${DATA_DIR}/${log}" "${RUN_DIR}/"
    fi
done

# 4. Generate SHA256 checksums for backup verification
echo "[INFO] Generating integrity checksums..."
cd "${RUN_DIR}"
find . -type f -exec sha256sum {} + > checksums.txt
cd - > /dev/null

# 5. Compress the backup run
TAR_FILE="${BACKUP_DIR}/solomon_backup_${TIMESTAMP}.tar.gz"
tar -czf "${TAR_FILE}" -C "${BACKUP_DIR}" "run_${TIMESTAMP}"
rm -rf "${RUN_DIR}"

# 6. Verify backup tarball checksum
sha256sum "${TAR_FILE}" > "${TAR_FILE}.sha256"
echo "[INFO] Backup file saved: ${TAR_FILE}"

# 7. Apply retention policy (Keep last $RETENTION_COUNT archives)
echo "[INFO] Applying retention policy..."
cd "${BACKUP_DIR}"
# List tar.gz files sorted by time, oldest first, and delete excess
ls -t solomon_backup_*.tar.gz 2>/dev/null | tail -n +$((RETENTION_COUNT + 1)) | while read -r old_backup; do
    echo "  - Removing expired backup: ${old_backup}"
    rm -f "${old_backup}" "${old_backup}.sha256"
done
cd - > /dev/null

# 8. Update Last Successful Backup marker
echo "SUCCESS:${TIMESTAMP}:${TAR_FILE}" > "${BACKUP_DIR}/last_backup_status.txt"
echo "[INFO] Backup workflow completed successfully."
