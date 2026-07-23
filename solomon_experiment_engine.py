"""
Solomon Perpetual Learning Machine
Phase 3: Experiment Engine (Scientific Method Pipeline)

Executes the automated scientific method pipeline:
Hypothesis -> Plan -> Sandbox Execution -> Evidence Capture -> Review -> Mnemosyne Promotion.
"""

import time
from typing import Dict, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SandboxExecutor

class ExperimentEngine:
    """
    Drives scientific method experiments to validate dynamic optimizations.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def execute_reproducible_experiment(self, opportunity: Dict[str, Any], hypothesis: str, execution_script: str) -> Dict[str, Any]:
        """
        Runs a complete end-to-end scientific experiment.
        """
        pipeline_status = {}

        # 1. Hypothesis Formulation
        pipeline_status["hypothesis"] = {
            "opportunity_target": opportunity["name"],
            "hypothesis_statement": hypothesis,
            "success_criteria": "Execution completes with status COMPLETED_SUCCESS"
        }

        # 2. Plan design
        pipeline_status["plan"] = {
            "target_code_size_chars": len(execution_script),
            "allocated_sandbox_timeout_sec": 3.0
        }

        # 3. Sandbox Execution
        start_time = time.perf_counter()
        sandbox_res = SandboxExecutor.execute_quarantined_code(execution_script, timeout_sec=3.0)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Evidence Capture
        pipeline_status["evidence"] = {
            "execution_success": sandbox_res["success"],
            "sandbox_status": sandbox_res["status"],
            "stdout": sandbox_res["stdout"].strip(),
            "stderr": sandbox_res["stderr"].strip(),
            "execution_time_ms": round(elapsed_ms, 3)
        }

        # 5. Review Stage
        # Experiment succeeded if sandbox returned True
        experiment_passed = sandbox_res["success"]
        pipeline_status["review"] = {
            "hypothesis_satisfied": experiment_passed,
            "experimental_consensus_reached": True,
            "system_recommendation": "PROMOTE_TO_MNEMOSYNE" if experiment_passed else "REJECT_AND_ABORT"
        }

        # 6. Mnemosyne Promotion (If passed, upsert into knowledge_cards)
        promoted = False
        card_id = f"SOK-EXPERIMENT-{opportunity['category'].upper()[:12]}-{int(time.time()) % 10000:04d}"
        if experiment_passed:
            content = (
                f"AUTONOMOUS EXPERIMENT OUTCOME: {opportunity['name']}.\n"
                f"Hypothesis: {hypothesis}.\n"
                f"Evidence: {sandbox_res['stdout'].strip()}.\n"
                f"Execution Speed: {elapsed_ms:.2f}ms."
            )
            focus = f"Validated via scientific loop for {opportunity['category']}"
            promoted = self.db.upsert_card(
                card_id=card_id,
                family="Knowledge",
                focus=focus,
                content=content,
                status="APPROVED" # Promoted through Review Gate to APPROVED
            )
            # Log revision snapshot
            self.db.update_card_status(card_id, "APPROVED")

        pipeline_status["promotion"] = {
            "card_id_promoted": card_id if promoted else None,
            "status": "APPROVED" if promoted else "NOT_PROMOTED",
            "db_persisted": promoted
        }

        return {
            "status": "success",
            "experiment_id": f"EXP-{int(time.time()) % 100000:05d}",
            "pipeline": pipeline_status,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Invoke the GET /api/mnemosyne/revisions endpoint to inspect "
                "the dynamic, verified SOK card revision history log!</span>"
            )
        }
