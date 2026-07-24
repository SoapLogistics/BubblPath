"""
Scientific Experimentation Engine & Sandbox Verification (SOSS Phase 11)

This module implements the Experiment Engine representing the formal scientific method loop:
Hypothesis -> Plan -> Sandbox Execution -> Evidence Capture -> Review -> Mnemosyne Promotion.
"""

import time
import traceback
from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SandboxExecutor

class ExperimentEngine:
    """
    Executes automated scientific experiments against curiosity cards
    to verify dynamic capabilities inside isolated sandbox execution environments.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def execute_scientific_experiment(self, curiosity_card_id: str, code_under_test: str, test_call: str) -> Dict[str, Any]:
        """
        Orchestrates the entire SOK scientific experiment loop:
        1. Hypothesis extraction
        2. Plan formulation
        3. Isolated Sandbox Execution
        4. Evidence & Telemetry Capture
        5. Review Gate Verification
        6. Mnemosyne Card Promotion
        """
        start_time = time.time()

        # 1. Fetch curiosity card context (Hypothesis)
        card = self.db.get_card(curiosity_card_id)
        if not card:
            hypothesis = "Dynamic execution optimization of unverified processes."
        else:
            hypothesis = card["content"]

        plan = f"Execute sandboxed script with targeted calibration structures to resolve {curiosity_card_id}."

        # 2. Execution in Isolated Sandbox
        sandbox_result = SandboxExecutor.execute_safely(
            source_code=code_under_test,
            entry_function_call=test_call,
            timeout_sec=3.0
        )

        elapsed_latency_ms = round((time.time() - start_time) * 1000.0, 2)
        success = sandbox_result.get("success", False)

        # 3. Evidence capture
        evidence = {
            "sandbox_stdout": sandbox_result.get("captured_stdout", ""),
            "execution_error": sandbox_result.get("error", ""),
            "elapsed_latency_ms": elapsed_latency_ms,
            "success": success
        }

        # 4. Review Gate Validation Rules
        # Criteria: Must run successfully, latency must be under 2000ms, and zero compile errors
        verified = success and (elapsed_latency_ms < 2000.0)

        promotion_card_id = f"SOK-PROMOTED-{curiosity_card_id.replace('SOK-CURIOSITY-', '')}"

        if verified:
            status = "APPROVED / ACTIVE"
            # 5. Mnemosyne Promotion - Create a new high-confidence, verified SOK Procedure Card
            self.db.upsert_card(
                card_id=promotion_card_id,
                family="Procedure",
                focus=f"Verified Procedure: Resolution of {curiosity_card_id}",
                content=f"Successfully executed scientific trial in isolated sandbox with latency {elapsed_latency_ms}ms. Evidence: {sandbox_result.get('captured_stdout', '').strip()}"
            )
            # Update source card confidence
            self.db.update_card_confidence(curiosity_card_id, "success", learning_rate=0.1)
            # Add relationship link
            self.db.add_link(promotion_card_id, curiosity_card_id, "SUPERSEDES")
        else:
            status = "FAILED / REJECTED"
            # If failed, compile SOK Failure Card and scale confidence down
            self.db.upsert_card(
                card_id=promotion_card_id,
                family="Failure",
                focus=f"Experiment Failed for {curiosity_card_id}",
                content=f"Scientific trial rejected. Error: {sandbox_result.get('error', '')}"
            )
            self.db.update_card_confidence(curiosity_card_id, "failure", learning_rate=0.1)
            self.db.add_link(promotion_card_id, curiosity_card_id, "DOCUMENTS_FAILURE")

        return {
            "curiosity_card_id": curiosity_card_id,
            "hypothesis": hypothesis,
            "plan_formulated": plan,
            "sandbox_evidence": evidence,
            "review_gate_status": status,
            "promoted_card_id": promotion_card_id,
            "promoted_card_saved": True
        }
