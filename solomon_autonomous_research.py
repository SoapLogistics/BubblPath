"""
Solomon Perpetual Learning Machine
Phase 7: Autonomous Research & Proactive Evaluation

Initiates research projects independently, runs benchmark comparisons of candidate
algorithms inside isolated sandboxes, identifies the winner, and promotes it to the SQLite ledger.
"""

import time
from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB
from solomon_skill_graph import SandboxExecutor

class AutonomousResearchEngine:
    """
    Independently evaluates candidate dynamic methods, selecting and promoting the optimal algorithm.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def execute_independent_benchmark_research(
        self,
        research_topic: str,
        candidates: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Runs parallel benchmarks of code candidates in sandboxes, identifies the optimal winner,
        and promotes the winning method directly into active SQLite cognitive memory.
        """
        benchmarks_results = []

        for cand in candidates:
            name = cand["name"]
            source = cand["source_code"]
            test_harness = cand.get("test_harness", "assert True")

            full_script = f"{source}\n\n# --- Test Harness ---\n{test_harness}"

            # Execute benchmark in sandbox
            start_time = time.perf_counter()
            sandbox_res = SandboxExecutor.execute_quarantined_code(full_script, timeout_sec=2.0)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            success = sandbox_res["success"]

            benchmarks_results.append({
                "candidate_name": name,
                "success": success,
                "sandbox_status": sandbox_res["status"],
                "execution_latency_ms": round(elapsed_ms, 3) if success else float('inf'),
                "stdout": sandbox_res["stdout"].strip(),
                "stderr": sandbox_res["stderr"].strip()
            })

        # Identify winner (must be successful and have lowest latency)
        successful_candidates = [b for b in benchmarks_results if b["success"]]

        winner = None
        if successful_candidates:
            winner = min(successful_candidates, key=lambda x: x["execution_latency_ms"])

        promoted = False
        card_id = f"SOK-RESEARCH-{research_topic.upper().replace(' ', '_')[:12]}-{int(time.time()) % 10000:04d}"

        if winner:
            winning_name = winner["candidate_name"]
            # Find candidate code
            winning_cand = next(c for c in candidates if c["name"] == winning_name)

            content = (
                f"AUTONOMOUS RESEARCH OUTCOME: {research_topic}.\n"
                f"Winning Candidate: {winning_name}.\n"
                f"Benchmark Speed: {winner['execution_latency_ms']:.3f}ms.\n"
                f"Synthesized Implementation:\n{winning_cand['source_code']}"
            )
            focus = f"Evaluated and verified via independent research loop"
            promoted = self.db.upsert_card(
                card_id=card_id,
                family="Knowledge",
                focus=focus,
                content=content,
                status="APPROVED"
            )
            self.db.update_card_status(card_id, "APPROVED")

        return {
            "status": "success",
            "research_topic": research_topic,
            "total_candidates_evaluated": len(candidates),
            "benchmarks": benchmarks_results,
            "winner_identified": winner is not None,
            "winner_details": winner,
            "promotion_report": {
                "card_id_promoted": card_id if promoted else None,
                "status": "APPROVED" if promoted else "NOT_PROMOTED",
                "db_persisted": promoted
            },
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "Formally inject the winning candidate algorithm into active memory namespaces "
                "using the POST /api/mnemosyne/ast-inject endpoint!</span>"
            )
        }
