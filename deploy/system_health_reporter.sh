#!/usr/bin/env bash
# ==============================================================================
# Solomon System Health and Cross-Machine Dependency Reporter
# ==============================================================================
set -euo pipefail

REPORT_FILE="/var/log/solomon_health_report.json"
CURRENT_MACHINE=$(hostname)

echo "[INFO] Running Solomon System Health Scanner on ${CURRENT_MACHINE}..."

# 1. Gather resource usage metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
DISK_FREE_OPT=$(df -h /opt/solomon 2>/dev/null | tail -n 1 | awk '{print $4}') || DISK_FREE_OPT="N/A"
DISK_FREE_ROOT=$(df -h / | tail -n 1 | awk '{print $4}')

# 2. Check local SOSS service status
SERVICE_ACTIVE=$(systemctl is-active solomon-soss 2>/dev/null || echo "inactive")

# 3. Check cross-machine connections over Tailscale
SS1_PING=$(ping -c 1 -W 2 ss1-machine.tailscale 2>/dev/null && echo "ONLINE" || echo "OFFLINE")
SS2_PING=$(ping -c 1 -W 2 ss2-machine.tailscale 2>/dev/null && echo "ONLINE" || echo "OFFLINE")
SS3_PING=$(ping -c 1 -W 2 ss3-machine.tailscale 2>/dev/null && echo "ONLINE" || echo "OFFLINE")

# 4. Read last backup status
LAST_BACKUP="UNKNOWN"
if [ -f "/var/backups/solomon/last_backup_status.txt" ]; then
    LAST_BACKUP=$(cat /var/backups/solomon/last_backup_status.txt)
fi

# 5. Build and write the JSON health report
cat <<EOF > "${REPORT_FILE}"
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "hostname": "${CURRENT_MACHINE}",
  "service_status": "${SERVICE_ACTIVE}",
  "metrics": {
    "cpu_usage_percent": ${CPU_USAGE},
    "disk_free_root": "${DISK_FREE_ROOT}",
    "disk_free_opt_solomon": "${DISK_FREE_OPT}"
  },
  "connectivity": {
    "ss1_status": "${SS1_PING}",
    "ss2_status": "${SS2_PING}",
    "ss3_status": "${SS3_PING}"
  },
  "backup": {
    "last_backup_record": "${LAST_BACKUP}"
  }
}
EOF

echo "[INFO] Health report written successfully to ${REPORT_FILE}."
