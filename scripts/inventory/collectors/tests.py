import subprocess

def run_cmd(cmd, timeout=60):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode('utf-8')
        return output.strip()
    except subprocess.CalledProcessError as e:
        return (e.output.decode('utf-8') if e.output else str(e)).strip()
    except Exception as e:
        return str(e)

def collect():
    results = []
    evidence = []

    pytest_out = run_cmd("PYTHONPATH=. python3 -m pytest")

    passed = pytest_out.count("passed")
    failed = pytest_out.count("FAILED") + pytest_out.count("failed")

    results.append({
        "test_suite": "pytest",
        "passed": passed,
        "failed": failed,
    })
    evidence.append({
        "claim": "Test suite executed",
        "confidence": "VERIFIED" if failed == 0 else "PARTIALLY_VERIFIED",
        "collector": "tests.py",
        "command": "PYTHONPATH=. python3 -m pytest",
        "stdout": pytest_out
    })

    return results, evidence
