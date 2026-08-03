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

    docker_ps = run_cmd("docker ps || echo 'docker not available'")
    status = "Available" if "CONTAINER ID" in docker_ps else "Not Available"
    count = str(docker_ps.count('\n')) if status == "Available" else "0"

    results.append({
        "status": status,
        "containers": count
    })
    evidence.append({
        "claim": "Docker daemon running",
        "confidence": "VERIFIED" if status == "Available" else "CONTRADICTED",
        "collector": "docker.py",
        "command": "docker ps",
        "stdout": docker_ps
    })

    return results, evidence
