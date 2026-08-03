import subprocess

def run_cmd(cmd, timeout=30):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode('utf-8')
        return output.strip()
    except Exception as e:
        return str(e)

def collect(hosts=["localhost"]):
    results = []
    evidence = []

    for h in hosts:
        if h == "localhost":
            hostname = run_cmd("hostname")
            uptime = run_cmd("uptime -p")
            kernel = run_cmd("uname -a")
            results.append({
                "hostname": hostname,
                "reachability": "Local",
                "uptime": uptime,
                "kernel": kernel
            })
            evidence.append({"claim": "Host is up", "confidence": "VERIFIED", "collector": "host.py", "command": "uptime -p", "stdout": uptime})
        else:
            reachability = "Reachable" if "0% packet loss" in run_cmd(f"ping -c 1 -W 1 {h}") else "Unreachable"
            results.append({
                "hostname": h,
                "reachability": reachability,
            })
            evidence.append({"claim": f"Host {h} pinged", "confidence": "VERIFIED" if reachability == "Reachable" else "UNVERIFIED", "collector": "host.py", "command": f"ping -c 1 -W 1 {h}", "stdout": ""})

    return results, evidence
