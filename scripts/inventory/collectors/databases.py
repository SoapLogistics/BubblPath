import subprocess
import os

def run_cmd(cmd, timeout=60):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode('utf-8')
        return output.strip()
    except subprocess.CalledProcessError as e:
        return ""
    except Exception as e:
        return ""

def collect(paths=["/home", "/app", "/srv"]):
    results = []
    evidence = []

    for loc in paths:
        if os.path.exists(loc):
            db_files = run_cmd(f"find {loc} -maxdepth 5 -type f \\( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \\) 2>/dev/null").split('\n')
            for db in db_files:
                if not db: continue
                sz = run_cmd(f"ls -lh {db} | awk '{{print $5}}'")
                results.append({"path": db, "size": sz, "status": "Found"})

                evidence.append({
                    "claim": f"Database found: {db}",
                    "confidence": "VERIFIED",
                    "collector": "databases.py",
                    "command": f"ls -lh {db}",
                    "stdout": sz
                })

    return results, evidence
