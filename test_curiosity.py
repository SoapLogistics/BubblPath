"""
Unit tests for Solomon SOSS Phase 2: Curiosity Engine (Prometheus Opportunity Mapper)
"""

import pytest
from solomon_curiosity_engine import CuriosityEngine, LearningOpportunity


class TestCuriosityEngine:
    """
    Verifies Curiosity Engine opportunity weighting formulas and log scanners.
    """

    def test_calculate_lo_score_standard(self):
        engine = CuriosityEngine(w_v=1.0, w_d=1.0, w_u=1.0, w_r=1.0, w_c=1.0)
        lo = LearningOpportunity(
            task_id="LO-STD-1",
            title="Optimizing DB",
            description="Speed up SQLite writing.",
            value=8.0,
            difficulty=4.0,
            future_use=9.0,
            risk=2.0,
            compute_cost=3.0,
            is_absurd=False
        )
        score = engine.calculate_lo_score(lo)
        # Expected score: 1.0*8.0 + 1.0*4.0 + 1.0*9.0 - 1.0*2.0 - 1.0*3.0 = 8 + 4 + 9 - 2 - 3 = 16.0
        assert score == 16.0
        assert lo.lo_score == 16.0

    def test_calculate_lo_score_einstein_absurdity(self):
        """
        Asserts that an absurd idea gets Einstein absurdity multipliers and bonus points.
        """
        engine = CuriosityEngine(w_v=1.0, w_d=1.0, w_u=1.0, w_r=1.0, w_c=1.0)
        lo = LearningOpportunity(
            task_id="LO-ABSURD-1",
            title="Quantize to -1 bit",
            description="Highly unconventional compression technique.",
            value=8.0,
            difficulty=4.0,
            future_use=9.0,
            risk=2.0,
            compute_cost=3.0,
            is_absurd=True
        )
        score = engine.calculate_lo_score(lo)
        # Standard terms:
        # val = 1.0*8.0 = 8.0
        # diff = 1.0*4.0 = 4.0
        # util = 1.0 * 9.0 * 1.8 = 16.2 (Einstein bonus)
        # risk = 1.0 * 2.0 * 0.4 = 0.8 (Einstein risk mitigation)
        # comp = 1.0*3.0 = 3.0
        # absurdity_bonus = 5.0
        # Expected score: 8.0 + 4.0 + 16.2 - 0.8 - 3.0 + 5.0 = 29.4
        assert abs(score - 29.4) < 0.01

    def test_get_priority_queue(self):
        engine = CuriosityEngine()
        lo1 = LearningOpportunity("T1", "Easy Standard", "Desc", 4, 2, 4, 2, 1, False)
        lo2 = LearningOpportunity("T2", "Hard Absurd", "Desc", 8, 9, 8, 8, 4, True)

        engine.register_opportunity(lo1)
        engine.register_opportunity(lo2)

        queue = engine.get_priority_queue()
        assert len(queue) == 2
        # Absurd breakthrough task should be ranked higher due to Einstein multiplier bonuses
        assert queue[0].task_id == "T2"

    def test_scan_feedback_for_gaps(self):
        engine = CuriosityEngine()
        logs = [
            {"event_type": "EXECUTION", "outcome": "success", "feature_name": "Inference"},
            {"event_type": "RECURSIVE_CRUCIBLE_FAIL", "outcome": "failure", "error_msg": "Timeout on layer 4", "feature_name": "QuantSolver"}
        ]
        gaps = engine.scan_feedback_for_gaps(logs)
        assert len(gaps) == 1
        assert gaps[0].title == "Repair and Assimilate QuantSolver"
        assert gaps[0].value == 8.5
