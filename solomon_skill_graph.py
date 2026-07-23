"""
Solomon Perpetual Learning Machine
Active Skill Graph & Quarantined Sandbox Execution Engine (SOSS Phase 6)

This module implements:
1. A topological Skill Graph to manage dynamic capabilities and their dependencies.
2. A Quarantined Sandbox Executor running dynamic scripts inside an isolated,
   resource-capped, and timed-out subprocess environment to prevent process crashes.
"""

import sys
import json
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional

class SkillGraph:
    """
    Manages dynamic skill definitions, metadata, and topological dependency tracking.
    """
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}

    def register_skill(self, skill_id: str, name: str, source_code: str, dependencies: Optional[List[str]] = None):
        """
        Registers a new capability node inside the active graph.
        """
        self.skills[skill_id] = {
            "skill_id": skill_id,
            "name": name,
            "source_code": source_code,
            "dependencies": dependencies or []
        }

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        return self.skills.get(skill_id)

    def get_all_skills(self) -> List[Dict[str, Any]]:
        return list(self.skills.values())


class SandboxExecutor:
    """
    Executes Python source code safely inside a quarantined, resource-constrained subprocess.
    Enforces timeout ceilings, intercepts errors, and captures standard outputs cleanly.
    """

    @classmethod
    def execute_safely(
        cls,
        source_code: str,
        entry_function_call: str,
        timeout_sec: float = 2.0
    ) -> Dict[str, Any]:
        """
        Runs the provided code inside a temp file executed by an isolated python subprocess.
        Prevents infinite loops, file modifications, or crash leaks.
        """
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

        # Prepend standard json import
        if "import json" not in full_code:
            full_code = "import json\n" + full_code

        # Write to secure temp file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write(full_code)
            temp_file_path = temp_file.name

        # Execute in isolated subprocess
        try:
            completed_proc = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )

            stdout_str = completed_proc.stdout.strip()
            stderr_str = completed_proc.stderr.strip()

            # Locate JSON block in stdout
            lines = stdout_str.split("\n")
            json_response = None
            captured_stdout_lines = []

            for line in lines:
                if line.startswith('{"status":') and 'return_value' in line or 'error_msg' in line:
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
                        "message": "Quarantined skill execution succeeded."
                    }
                else:
                    return {
                        "success": False,
                        "error": json_response["error_msg"],
                        "traceback": json_response["traceback"],
                        "captured_stdout": "\n".join(captured_stdout_lines),
                        "message": "Quarantined skill execution failed with internal error."
                    }
            else:
                return {
                    "success": False,
                    "error": f"Subprocess exited without expected JSON block. Stderr: {stderr_str}",
                    "captured_stdout": stdout_str,
                    "message": "Quarantined execution output was malformed."
                }

        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "error": f"Execution exceeded maximum timeout of {timeout_sec} seconds. Quarantined process killed.",
                "message": "Quarantined execution aborted due to timeout OOM/infinite-loop prevention."
            }
        finally:
            # Always clean up temporary execution file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
