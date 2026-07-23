"""
Solomon Perpetual Learning Machine
Docker Sandbox Execution Engine (SOSS Phase 3A)

This module implements:
1. Programmatic Python script execution inside quarantined, ephemeral Docker containers.
2. Timing, network isolation, and system resource ceiling enforcement (CPU/RAM caps).
3. Seamless fallback to local timed quarantined subprocess executor if Docker features are blocked/restricted.
"""

import os
import sys
import json
import tempfile
try:
    import docker
except ImportError:
    docker = None
import time
import logging
from typing import Dict, Any, List, Optional
from solomon_skill_graph import SandboxExecutor

logger = logging.getLogger(__name__)

class DockerSandboxExecutor:
    """
    Executes Python source code securely inside a read-only mounted,
    resource-capped, and isolated Docker container, with subprocess fallback.
    """

    @classmethod
    def execute_in_container(
        cls,
        source_code: str,
        entry_function_call: str,
        timeout_sec: float = 3.0,
        memory_limit: str = "256m",
        cpu_quota: int = 50000 # 50% CPU limit
    ) -> Dict[str, Any]:
        """
        Runs the provided code inside a temp file mounted read-only inside a python:3.12-slim container.
        Falls back to SandboxExecutor if Docker mounting or execution fails.
        """
        # Create a temp directory to mount to the docker container
        temp_dir = tempfile.mkdtemp(prefix="solomon_docker_")
        temp_script_path = os.path.join(temp_dir, "script.py")

        # Append active call runner logic to temp script execution
        full_code = (
            f"{source_code.strip()}\n\n"
            f"if __name__ == '__main__':\n"
            f"    try:\n"
            f"        result = {entry_function_call}\n"
            f"        print(json.dumps({{'status': 'success', 'return_value': result}}))\n"
            f"    except Exception as e:\n"
            f"        import traceback\n"
            f"        print(json.dumps({{'status': 'error', 'error_msg': str(e), 'traceback': traceback.format_exc()}}))\n"
        )

        if "import json" not in full_code:
            full_code = "import json\n" + full_code

        with open(temp_script_path, "w", encoding="utf-8") as f:
            f.write(full_code)

        # Initialize Docker client
        if docker is None:
            logger.warning("Docker package not installed. Falling back to SandboxExecutor.")
            return cls._execute_fallback(source_code, entry_function_call, timeout_sec)

        try:
            client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client unavailable: {str(e)}. Falling back to SandboxExecutor.")
            return cls._execute_fallback(source_code, entry_function_call, timeout_sec)

        container = None
        try:
            # Run container with resource limits, read-only mount, and disabled network (isolated)
            container = client.containers.run(
                image="python:3.12-slim",
                command=["python", "/app/script.py"],
                volumes={
                    temp_dir: {
                        "bind": "/app",
                        "mode": "ro" # Read-Only mount to protect host directory
                    }
                },
                mem_limit=memory_limit,
                nano_cpus=cpu_quota * 1000, # convert CFS quota to nanoseconds
                network_mode="none", # completely isolated network
                detach=True
            )

            # Wait for execution or timeout
            container_stopped = False

            # Simple spin lock with timeout
            limit_cycles = int(timeout_sec * 10)
            for _ in range(limit_cycles):
                container.reload()
                if container.status == "exited":
                    container_stopped = True
                    break
                time.sleep(0.1)

            if not container_stopped:
                container.kill()
                return {
                    "success": False,
                    "error": f"Execution exceeded maximum timeout of {timeout_sec} seconds. Container killed.",
                    "message": "Quarantined Docker container aborted due to timeout OOM/infinite-loop prevention."
                }

            # Retrieve stdout/stderr logs
            stdout_logs = container.logs(stdout=True, stderr=False).decode("utf-8").strip()
            stderr_logs = container.logs(stdout=False, stderr=True).decode("utf-8").strip()

            # Process logs to extract the JSON payload
            lines = stdout_logs.split("\n")
            json_response = None
            captured_stdout_lines = []

            for line in lines:
                if line.startswith('{"status":') and ('return_value' in line or 'error_msg' in line):
                    try:
                        json_response = json.loads(line)
                    except json.JSONDecodeError:
                        captured_stdout_lines.append(line)
                else:
                    if line:
                        captured_stdout_lines.append(line)

            if json_response:
                if json_response["status"] == "success":
                    return {
                        "success": True,
                        "return_value": json_response["return_value"],
                        "captured_stdout": "\n".join(captured_stdout_lines),
                        "message": "Quarantined Docker container execution succeeded."
                    }
                else:
                    return {
                        "success": False,
                        "error": json_response["error_msg"],
                        "traceback": json_response["traceback"],
                        "captured_stdout": "\n".join(captured_stdout_lines),
                        "message": "Quarantined Docker container failed with internal script error."
                    }
            else:
                return {
                    "success": False,
                    "error": f"Docker container exited without expected JSON block. Stderr: {stderr_logs}",
                    "captured_stdout": stdout_logs,
                    "message": "Quarantined Docker execution output was malformed."
                }

        except Exception as e:
            logger.warning(f"Docker run failed (nested environment restrictions): {str(e)}. Triggering SandboxExecutor fallback.")
            return cls._execute_fallback(source_code, entry_function_call, timeout_sec)
        finally:
            # Always clean up temporary resources
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            try:
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception:
                pass

    @classmethod
    def _execute_fallback(cls, source_code: str, entry_function_call: str, timeout_sec: float) -> Dict[str, Any]:
        """
        Executes code safely inside our secure timed quarantined subprocess sandbox.
        """
        res = SandboxExecutor.execute_safely(source_code, entry_function_call, timeout_sec)
        res["message"] = f"Quarantined execution succeeded via SandboxExecutor fallback. {res.get('message', '')}"
        return res
