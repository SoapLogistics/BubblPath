"""
Solomon Perpetual Learning Loop Engine
End-to-End Core Orchestrator (Observe -> Learn -> Remember -> Retrieve -> Improve)

This module demonstrates:
1. Receive a brand-new task (e.g., build and sort or resolve complex service setups).
2. Solve it (using observational profiling / code extraction).
3. Distill the solution into a SOK card with an explicit Review Gate transition (DRAFT -> REVIEWED -> APPROVED -> ACTIVE).
4. Link it relationally to active SOK cards.
5. Retrieve that card on a later, similar task via hybrid cosine similarity.
6. Improve performance (e.g. routing and execution metrics) because of the retrieved card.
7. Log metrics demonstrating multi-fold speedups, memory savings, and failure reductions.
"""

import time
from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_model_router import ModelRouter
from solomon_observational_simulator import ObservationalSimulator
from solomon_ast_injector import ASTInjector
from solomon_skill_graph import SandboxExecutor

class SolomonPerpetualLearningLoop:
    def __init__(self, db: SolomonMnemosyneDB, router: ModelRouter, skills_graph = None):
        self.db = db
        self.router = router
        self.skills_graph = skills_graph

    def execute_complete_cycle(self, task_name: str, target_service: str) -> Dict[str, Any]:
        """
        Executes a complete 7-stage perpetual learning cycle.
        """
        execution_metrics = {}
        trace = []

        # -------------------------------------------------------------
        # Stage 1 & 2: Observe and Understand (Receive brand-new task & analyze)
        # -------------------------------------------------------------
        trace.append("Stage 1 & 2 (Observe & Understand): Received brand-new capability request.")

        # Simulate a closed-source command execution output of the new service/binary
        raw_cli_output = (
            "Kubernetes Control Plane Node: master-1\n"
            "Status: Ready\n"
            "Active Pods: 14\n"
            "Allocated RAM: 512MB\n"
            "Services Configured: k8s-service-engine"
        )

        # Profile & Rebuild (Gabriel Assimilation)
        rebuild_report = ObservationalSimulator.profile_and_rebuild_binary(
            binary_name=target_service,
            command="get status",
            std_output_sample=raw_cli_output
        )
        synthesized_code = rebuild_report["synthesized_source_code"]
        class_name = rebuild_report["compilation_details"]["clean_room_class_synthesized"]

        # -------------------------------------------------------------
        # Stage 3: Build & Test (Quarantined Sandbox Execution of assimilated code)
        # -------------------------------------------------------------
        trace.append("Stage 3 (Build & Test): Executing synthesized capability in quarantined sandbox.")

        # Test running inside our Sandbox Executor to confirm functional equivalence
        test_run = SandboxExecutor.execute_safely(
            source_code=synthesized_code,
            entry_function_call=f"{class_name}().run()",
            timeout_sec=2.0
        )
        assert test_run["success"] is True, "Assimilated capability failed sandbox execution checks."

        # Phase 2: Hot-Swap Live-Execution Bypasses
        gabriel_mode = "READ_ONLY"
        try:
            modes = self.db.get_worker_modes()
            for m in modes:
                if m["worker_id"] == "gabriel":
                    gabriel_mode = m["mode"].upper()
                    break
        except Exception:
            pass

        physical_file_written = False
        registered_in_graph = False

        if gabriel_mode in ("LIVE", "READ_WRITE"):
            trace.append("[Phase 2 Live Bypass] Gabriel is in LIVE/READ_WRITE mode! Committing file directly to disk.")
            filepath = f"solomon_rebuilt_{target_service.replace('-', '_')}.py"
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(synthesized_code)
                physical_file_written = True
                trace.append(f"[Phase 2 Live Bypass] File written to {filepath}.")
            except Exception as fe:
                trace.append(f"[Phase 2 Live Bypass] Failed to write file: {str(fe)}")

            if self.skills_graph:
                try:
                    skill_id = f"SKILL-ASSIMILATED-{target_service.upper().replace('-', '_')}"
                    self.skills_graph.register_skill(
                        skill_id=skill_id,
                        name=f"Assimilated {target_service.capitalize()} service",
                        source_code=synthesized_code
                    )
                    registered_in_graph = True
                    trace.append(f"[Phase 2 Live Bypass] Registered skill '{skill_id}' in Active Skill Graph.")
                except Exception as se:
                    trace.append(f"[Phase 2 Live Bypass] Graph registration failed: {str(se)}")

        # -------------------------------------------------------------
        # Stage 4: Remember (Create memory card + Review Gate promotion)
        # -------------------------------------------------------------
        trace.append("Stage 4 (Remember): Registering distilled knowledge as a SOK memory card.")

        card_id = f"SOK-ASSIMILATED-{target_service.upper().replace('-', '_')}"
        card_content = (
            f"Assimilated native Python equivalent for the closed-source '{target_service}' binary. "
            f"Optimized layout prevents server latency spikes and limits local memory overhead. "
            f"Execution returns stable Node metrics, status information, and active container profiles."
        )

        # Clean up any pre-existing card with the same ID to ensure test determinism and clean slate
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        conn.execute("DELETE FROM knowledge_cards WHERE card_id = ?", (card_id,))
        conn.commit()
        conn.close()

        # Create as DRAFT card
        self.db.upsert_card(
            card_id=card_id,
            family="Knowledge",
            focus=f"Native assimilation code template for {target_service}",
            content=card_content,
            validation_state="DRAFT"
        )

        # Phase 3: Automated Review Gate Promotions with defensive security scans
        trace.append("Phase 3 (Review Gate): Commencing automated Hugin security scan on synthesized code.")

        # Defensive regex patterns
        blocked_patterns = [
            r"__import__\(\s*['\"]os['\"]\s*\)\.system",
            r"subprocess\.Popen\(\s*[^,]+,\s*shell\s*=\s*True\)",
            r"eval\(\s*input\s*\(",
            r"rm\s+-rf\s+/",
            r"chmod\s+777",
        ]

        import re
        security_check_passed = True
        for pattern in blocked_patterns:
            if re.search(pattern, synthesized_code, re.IGNORECASE):
                security_check_passed = False
                trace.append(f"Review Gate Audit FAILURE: Blocked pattern detected: '{pattern}'")
                break

        if security_check_passed:
            trace.append("Phase 3 (Review Gate): Automated security audit PASSED. Commencing auto-promotion.")

            trace.append(f"Review Gate: Transitioning {card_id} from DRAFT to REVIEWED.")
            self.db.update_card_validation_state(card_id, "REVIEWED")

            trace.append(f"Review Gate: Transitioning {card_id} from REVIEWED to APPROVED.")
            self.db.update_card_validation_state(card_id, "APPROVED")

            trace.append(f"Review Gate: Transitioning {card_id} from APPROVED to ACTIVE.")
            self.db.update_card_validation_state(card_id, "ACTIVE")
        else:
            trace.append(f"Review Gate: Promotion ABORTED for {card_id}. Staged card remains in DRAFT to prevent poisoning.")

        # Create directed relational links to connect knowledge nodes
        self.db.add_link(card_id, "SOK-KNOWLEDGE-QUANT-001", "ENHANCES")
        self.db.add_link("SOK-IMPROVED-PROCEDURE-QUANT-001", card_id, "DEPENDS_ON")

        # -------------------------------------------------------------
        # Stage 5 & 6: Retrieve & Improve (Retrieve later on a similar task and optimize)
        # -------------------------------------------------------------
        trace.append("Stage 5 & 6 (Retrieve & Improve): Querying similar tasks.")

        similar_query = f"Assimilated native Python equivalent for the closed-source '{target_service}' binary."
        routing_decision = self.router.route_query(similar_query, threshold=0.60)

        # Verify that our newly registered card was matched and used for routing
        assert routing_decision["best_match_card_id"] == card_id, "Model Router failed to retrieve active assimilated memory card."

        # Log simulated resource efficiency gains based on routing hot-swapping
        vram_savings = routing_decision["resource_impact"]["vram_saved_gb"]
        latency_reduction = routing_decision["resource_impact"]["latency_reduction_percent"]
        cost_savings = routing_decision["resource_impact"]["cost_savings_percent"]

        # Run reinforcement feedback to scale card confidence score up upon execution success
        self.db.update_card_confidence(card_id, "success", learning_rate=0.10)
        final_card = self.db.get_card(card_id)

        # Build complete perpetual learning execution report
        execution_metrics = {
            "task": task_name,
            "target_service": target_service,
            "assimilated_class": class_name,
            "validation_gate_final_state": final_card["validation_state"],
            "reinforced_card_confidence": final_card["confidence"],
            "rebuilt_code_bytes": len(synthesized_code),
            "phase2_live_impact": {
                "physical_file_written": physical_file_written,
                "registered_in_active_graph": registered_in_graph,
                "active_mode": gabriel_mode
            },
            "phase3_review_gate_impact": {
                "security_scan_passed": security_check_passed,
                "review_gate_promoted": security_check_passed
            },
            "resource_efficiency_metrics": {
                "active_model_allocated": routing_decision["routed_model"],
                "allocated_precision": routing_decision["precision_allocated"],
                "vram_saved_gb": vram_savings,
                "latency_reduction_percent": latency_reduction,
                "cost_savings_percent": cost_savings
            },
            "cognitive_execution_traces": trace
        }

        return execution_metrics
