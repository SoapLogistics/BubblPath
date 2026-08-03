import subprocess

def run_cmd(cmd, timeout=30):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode('utf-8')
        return output.strip()
    except Exception as e:
        return str(e)

def collect():
    results = []
    evidence = []

    failed_svcs = run_cmd("systemctl list-units --state=failed 2>/dev/null || echo 'systemctl not available'")

    results.append({
        "failed_services": failed_svcs
    })

    evidence.append({
        "claim": "Checked failed systemd services",
        "confidence": "PARTIALLY_VERIFIED",
        "collector": "services.py",
        "command": "systemctl list-units --state=failed",
        "stdout": failed_svcs
    })

    return results, evidence
