"""
Solomon Perpetual Learning Machine
Phase 2: Curiosity Engine (Prometheus Opportunity Mapper)

Discovers, ranks, and logs Learning Opportunities (LOs) based on execution logs,
active SQLite database focus fields, and system resource trends.
"""

from typing import Dict, List, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class PrometheusCuriosityEngine:
    """
    Scans logs and active database cards to identify, score, and rank Learning Opportunities.
    Implements the SOSS Opportunity Weighting Matrix.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db
        # Weighting coefficients
        self.w_v = 0.4  # Value weight
        self.w_d = 0.2  # Difficulty weight
        self.w_u = 0.3  # Future Use weight
        self.w_r = 0.2  # Risk weight
        self.w_c = 0.1  # Compute Cost weight

    def calculate_lo_score(self, value: float, difficulty: float, future_use: float, risk: float, compute_cost: float) -> float:
        """
        Calculates the SOSS Opportunity Score:
            LO_Score = w_v*Value + w_d*Difficulty + w_u*FutureUse - w_r*Risk - w_c*ComputeCost
        Scores are clipped to 2 decimal places.
        """
        raw_score = (self.w_v * value) + (self.w_d * difficulty) + (self.w_u * future_use) - (self.w_r * risk) - (self.w_c * compute_cost)
        return float(round(raw_score, 2))

    def scan_for_opportunities(self, simulated_rss_mb: float = 1400.0, simulated_sql_ms: float = 1.2) -> List[Dict[str, Any]]:
        """
        Scans system metrics and the active card database, generating a prioritized
        learning queue of opportunities.
        """
        opportunities = []

        # Baseline default opportunities
        opportunities.append({
            "name": "SpinQuant learned rotation optimization",
            "category": "quantization_optimization",
            "description": "Formulate learned orthogonal rotators to smooth outlier activation ranges in Layer 5.",
            "value": 9.5,
            "difficulty": 4.0,
            "future_use": 8.0,
            "risk": 1.5,
            "compute_cost": 3.0
        })

        opportunities.append({
            "name": "PagedAttention multi-tenant page allocation",
            "category": "ram_optimization",
            "description": "Apply physical block virtualization to pre-allocate KV cache in 4MB segments.",
            "value": 8.8,
            "difficulty": 6.0,
            "future_use": 9.0,
            "risk": 2.0,
            "compute_cost": 2.5
        })

        # Dynamic Opportunity 1: Heavy memory usage detected -> Trigger RAM Pruning
        if simulated_rss_mb > 1400.0:
            opportunities.append({
                "name": "AST AST-PRUNE memory compaction execution",
                "category": "resource_compaction",
                "description": f"Active memory footprint of {simulated_rss_mb:.1f}MB is approaching the 1.5GB cap. Refactor unused class caches.",
                "value": 9.0,
                "difficulty": 5.0,
                "future_use": 7.5,
                "risk": 1.0,
                "compute_cost": 1.5
            })

        # Dynamic Opportunity 2: DB Query speed evaluation -> Trigger SQL indexing rules
        if simulated_sql_ms > 1.0:
            opportunities.append({
                "name": "SQLite analytical schema vacuum and index optimize",
                "category": "database_speedup",
                "description": f"Query response average is {simulated_sql_ms:.3f}ms. Re-evaluate SQLite indices and execute VACUUM.",
                "value": 7.5,
                "difficulty": 3.0,
                "future_use": 6.0,
                "risk": 0.5,
                "compute_cost": 1.0
            })

        # Score and rank opportunities
        ranked_queue = []
        for opp in opportunities:
            score = self.calculate_lo_score(
                value=opp["value"],
                difficulty=opp["difficulty"],
                future_use=opp["future_use"],
                risk=opp["risk"],
                compute_cost=opp["compute_cost"]
            )
            opp["lo_score"] = score
            ranked_queue.append(opp)

        # Sort queue in descending order of lo_score
        ranked_queue.sort(key=lambda x: x["lo_score"], reverse=True)
        return ranked_queue
