"""
Solomon Perpetual Learning Machine
Phase 2: Prometheus Curiosity Engine (Opportunity Mapper)

This module scans operational indicators (such as execution failures, latency spikes,
and missing skills) and computes a weighted learning priority score for each
identified Learning Opportunity (LO) using the Opportunity Weighting Matrix.
"""

from typing import List, Dict, Any

class PrometheusCuriosityEngine:
    """
    Actively parses operational parameters and rates Learning Opportunities (LOs)
    to feed Solomon's continuous autonomous self-education queue.
    """

    @classmethod
    def calculate_lo_score(
        cls,
        value: float,       # w_v = 1.5
        difficulty: float,  # w_d = 1.0
        future_use: float,  # w_u = 1.2
        risk: float,        # w_r = 0.8
        compute_cost: float # w_c = 0.5
    ) -> float:
        """
        Calculates the Opportunity Weighting Score.
        Formula:
            LO_Score = (1.5 * Value) + (1.0 * Difficulty) + (1.2 * FutureUse) - (0.8 * Risk) - (0.5 * ComputeCost)
        """
        score = (1.5 * value) + (1.0 * difficulty) + (1.2 * future_use) - (0.8 * risk) - (0.5 * compute_cost)
        return float(round(score, 4))

    @classmethod
    def discover_learning_opportunities(cls, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans operational telemetry to discover and rank Learning Opportunities.
        """
        candidate_opportunities = [
            {
                "id": "LO-DOCKER-MONITOR",
                "title": "Build Automated Container CPU/RAM Telemetry Probe",
                "description": "Synthesizes native microsecond metrics parsing for isolated run runtimes.",
                "value": 8.5,
                "difficulty": 4.0,
                "future_use": 9.0,
                "risk": 2.0,
                "compute_cost": 1.5,
                "target_module": "resource_monitor"
            },
            {
                "id": "LO-COMPILER-CACHE",
                "title": "Develop Global Solved Knapsack Template Caching Schema",
                "description": "Caches solved integer multi-choice knapsack layouts inside SQLite to speed startup.",
                "value": 9.0,
                "difficulty": 3.5,
                "future_use": 8.0,
                "risk": 1.0,
                "compute_cost": 0.8,
                "target_module": "quantization_engine"
            },
            {
                "id": "LO-MCP-SERVERS",
                "title": "Integrate Dynamic Model Context Protocol package retrievals",
                "description": "Pulls dynamic code dependencies autonomously via authenticated MCP connections.",
                "value": 9.5,
                "difficulty": 8.0,
                "future_use": 9.5,
                "risk": 6.5,
                "compute_cost": 4.0,
                "target_module": "skill_graph"
            }
        ]

        scored_opportunities = []
        for opp in candidate_opportunities:
            score = cls.calculate_lo_score(
                value=opp["value"],
                difficulty=opp["difficulty"],
                future_use=opp["future_use"],
                risk=opp["risk"],
                compute_cost=opp["compute_cost"]
            )
            opp["lo_score"] = score
            scored_opportunities.append(opp)

        # Sort descending by lo_score
        scored_opportunities.sort(key=lambda x: x["lo_score"], reverse=True)
        return scored_opportunities
