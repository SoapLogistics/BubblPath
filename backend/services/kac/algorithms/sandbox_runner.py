import subprocess
import os
import uuid
from typing import Dict, Any

class SandboxRunner:
    """
    Safely executes algorithm test code in an isolated subprocess.
    """
    def run_test(self, python_code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
        """
        Executes code using a subprocess with restricted resources (stubbed for safety in testing).
        In a full deployment this should use Docker or a secure sandbox like gVisor.
        """
        # Ensure we use a unique temporary file per test to avoid race conditions
        test_file = f"/tmp/sandbox_test_{uuid.uuid4().hex}.py"
        with open(test_file, "w") as f:
            f.write(python_code)

        try:
            # Use basic safety wrapping:
            # In production, wrap this in unshare, docker, or bwrap for real isolation.
            # Here we enforce a strict timeout to prevent unbounded consumption.
            result = subprocess.run(
                ["python3", test_file],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env={"PYTHONUNBUFFERED": "1"} # Minimal safe env
            )

            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "failed", "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": f"Execution exceeded {timeout_seconds} seconds"}
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
