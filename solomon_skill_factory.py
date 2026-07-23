"""
Solomon Perpetual Learning Machine
Phase 4: Skill Factory (Gabriel Re-engineered)

Synthesizes, templates, validates, and registers highly structured,
modular, and benchmarked Skill Packages.
"""

from typing import Dict, List, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SandboxExecutor

class SkillPackage:
    """
    Encapsulates a modular Dynamic Skill Package with inputs, outputs, implementation, and tests.
    """

    def __init__(
        self,
        name: str,
        purpose: str,
        inputs: Dict[str, str],
        outputs: str,
        source_code: str,
        unit_tests: str,
        safety_constraints: Dict[str, Any] = None
    ):
        self.name = name
        self.purpose = purpose
        self.inputs = inputs
        self.outputs = outputs
        self.source_code = source_code
        self.unit_tests = unit_tests
        self.safety_constraints = safety_constraints or {"max_memory_mb": 250, "timeout_sec": 3.0}

    def compile_full_test_script(self) -> str:
        """
        Combines implementation source code with unit test assertions into a unified executable script.
        """
        return (
            f"{self.source_code}\n\n"
            "# --- Automated Unit Tests Assertion Block ---\n"
            f"{self.unit_tests}"
        )


class SkillFactory:
    """
    Compiles, validates, and registers SkillPackages into active system memory.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def validate_and_register_skill(self, package: SkillPackage) -> Dict[str, Any]:
        """
        Executes a skill package's unit tests inside a sandbox, asserts outcomes,
        and registers verified packages directly as active SQLite SOK cards.
        """
        test_script = package.compile_full_test_script()
        timeout = package.safety_constraints.get("timeout_sec", 3.0)

        # Execute tests inside quarantined sandbox
        sandbox_res = SandboxExecutor.execute_quarantined_code(test_script, timeout_sec=timeout)

        validated = sandbox_res["success"]
        promoted = False
        card_id = f"SOK-SKILL-{package.name.upper().replace('-', '_')}"

        if validated:
            # Format content card
            content = (
                f"MODULAR SKILL PACKAGE: {package.name}\n"
                f"Purpose: {package.purpose}\n"
                f"Inputs: {package.inputs}\n"
                f"Outputs: {package.outputs}\n"
                f"Source Implementation Hash: {hash(package.source_code)}"
            )
            focus = f"Verified modular Skill Package registration"
            promoted = self.db.upsert_card(
                card_id=card_id,
                family="Procedure",
                focus=focus,
                content=content,
                status="ACTIVE" # Active for immediate execution
            )
            self.db.update_card_status(card_id, "ACTIVE")

        return {
            "status": "success" if validated else "failed_validation",
            "skill_name": package.name,
            "unit_test_passed": validated,
            "sandbox_status": sandbox_res["status"],
            "stdout": sandbox_res["stdout"].strip(),
            "stderr": sandbox_res["stderr"].strip(),
            "db_registered": promoted,
            "card_id": card_id if promoted else None,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Incorporate this validated skill node into your active topological SkillGraph "
                "to automate step-by-step dependency resolution!</span>"
            )
        }
