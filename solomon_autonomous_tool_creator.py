"""
Solomon Perpetual Learning Machine
Phase 8: Autonomous Tool Creation

Identifies capability gaps, prototypes python tools, subjects them to AST and safety audits,
and registers verified tools as active reusable skills.
"""

import ast
from typing import Dict, List, Any, Tuple
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SandboxExecutor

class AutonomousToolCreator:
    """
    Autonomously prototypes, safety-audits, and registers new operational capabilities.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def audit_tool_safety(self, source_code: str) -> Tuple[bool, str]:
        """
        Parses python source code into an AST representation to audit safety constraints.
        Blocks imports of risky modules or calling dangerous builtins.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return False, f"AST compilation failed with SyntaxError: {str(e)}"

        # Set of blocked modules and dangerous functions
        blocked_imports = {"os", "subprocess", "shutil", "socket", "sys", "ctypes", "pty"}
        blocked_calls = {"eval", "exec", "open", "compile", "globals", "locals"}

        for node in ast.walk(tree):
            # Check direct imports (e.g. import os)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in blocked_imports:
                        return False, f"Safety violation: Blocked import '{alias.name}' detected!"

            # Check from-imports (e.g. from os import system)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in blocked_imports:
                    return False, f"Safety violation: Blocked import-from '{node.module}' detected!"

            # Check dangerous call names
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in blocked_calls:
                        return False, f"Safety violation: Dangerous builtin call '{node.func.id}' detected!"

        return True, "AST safety audit passed. No disallowed modules or builtins detected."

    def prototype_and_register_tool(
        self,
        tool_name: str,
        purpose: str,
        inputs: Dict[str, str],
        outputs: str,
        source_code: str,
        unit_tests: str
    ) -> Dict[str, Any]:
        """
        Runs safety constraints analysis, compiles unit tests in sandboxes, and registers the verified tool.
        """
        # 1. Run safety AST audit
        safe, msg = self.audit_tool_safety(source_code)
        if not safe:
            return {
                "status": "safety_violation",
                "tool_name": tool_name,
                "message": msg,
                "verified": False,
                "db_registered": False
            }

        # 2. Compile test runner
        full_script = f"{source_code}\n\n# --- Test Harness ---\n{unit_tests}"
        sandbox_res = SandboxExecutor.execute_quarantined_code(full_script, timeout_sec=2.0)

        validated = sandbox_res["success"]
        promoted = False
        card_id = f"SOK-TOOL-{tool_name.upper().replace('-', '_')}"

        if validated:
            content = (
                f"AUTONOMOUS GENERATED TOOL: {tool_name}\n"
                f"Purpose: {purpose}\n"
                f"Inputs: {inputs}\n"
                f"Outputs: {outputs}\n"
                f"AST Safety Audit: PASSED\n"
                f"Source:\n{source_code}"
            )
            focus = f"Verified autonomous tool creation"
            promoted = self.db.upsert_card(
                card_id=card_id,
                family="Procedure",
                focus=focus,
                content=content,
                status="ACTIVE"
            )
            self.db.update_card_status(card_id, "ACTIVE")

        return {
            "status": "success" if validated else "failed_tests",
            "tool_name": tool_name,
            "verified": validated,
            "sandbox_status": sandbox_res["status"],
            "stdout": sandbox_res["stdout"].strip(),
            "stderr": sandbox_res["stderr"].strip(),
            "db_registered": promoted,
            "card_id": card_id if promoted else None,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Formally map this verified capability in your central topological SkillGraph "
                "to instantly unlock reusable, recursive step pipelines!</span>"
            )
        }
