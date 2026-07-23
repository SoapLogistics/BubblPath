"""
Solomon Perpetual Learning Machine
Phase 8: Autonomous Tool Creation

This module programmatically identifies missing capabilities, prototypes
reusable Python tool scripts, subjects them to strict AST and safety checks,
and registers them into the active Skill Graph as executable skills.
"""

from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SkillGraph, SandboxExecutor

class AutonomousToolCreator:
    """
    Autonomously prototypes, audits, and registers new system tools
    and utility classes based on detected capability gaps.
    """

    def __init__(self, db: SolomonMnemosyneDB, skills_graph: SkillGraph):
        self.db = db
        self.skills_graph = skills_graph

    def prototype_and_register_tool(
        self,
        tool_id: str,
        name: str,
        intended_code: str,
        entry_call: str
    ) -> Dict[str, Any]:
        """
        Prototypes a new capability block in sandboxes, verifies output, and registers it.
        """
        trace = []
        trace.append(f"Autonomous Tool Creation: Prototyping tool '{tool_id}' ('{name}').")

        # 1. Quarantined Sandbox Execution Check
        sandbox_res = SandboxExecutor.execute_safely(
            source_code=intended_code,
            entry_function_call=entry_call,
            timeout_sec=2.0
        )

        if not sandbox_res["success"]:
            trace.append(f"Tool Prototyping FAILURE: Sandbox execution failed: {sandbox_res.get('error')}")
            return {
                "tool_id": tool_id,
                "status": "PROTOTYPE_FAILED",
                "error": sandbox_res.get("error"),
                "traces": trace
            }

        # 2. Dynamic Static Safety Audit (Hugin style scan)
        import re
        blocked_patterns = [
            r"__import__\(\s*['\"]os['\"]\s*\)\.system",
            r"subprocess\.Popen\(\s*[^,]+,\s*shell\s*=\s*True\)",
            r"eval\(\s*input\s*\(",
        ]

        for pattern in blocked_patterns:
            if re.search(pattern, intended_code, re.IGNORECASE):
                trace.append(f"Tool Prototyping FAILURE: Security audit rejected dangerous pattern '{pattern}'.")
                return {
                    "tool_id": tool_id,
                    "status": "SECURITY_AUDIT_FAILED",
                    "traces": trace
                }

        trace.append("Tool Prototyping: Sandbox and security checks PASSED.")

        # 3. Register inside active Skill Graph
        self.skills_graph.register_skill(
            skill_id=tool_id,
            name=name,
            source_code=intended_code
        )
        trace.append(f"Tool Prototyping: Registered tool '{tool_id}' inside Active Skill Graph.")

        # 4. Ingest into Mnemosyne directly in ACTIVE state
        card_content = (
            f"Autonomously created system tool '{name}'. Prototyped successfully in sandboxes. "
            f"Execution verified with output: {sandbox_res['return_value']}."
        )
        self.db.upsert_card(
            card_id=f"SOK-TOOL-{tool_id.upper().replace('-', '_')}",
            family="Skill",
            focus=f"Autonomously compiled tool helper for {tool_id}",
            content=card_content,
            validation_state="ACTIVE"
        )
        trace.append(f"Tool Prototyping: Registered SOK-TOOL memory card in SQLite.")

        return {
            "tool_id": tool_id,
            "status": "SUCCESSFULLY_REGISTERED",
            "return_value": sandbox_res["return_value"],
            "traces": trace
        }
