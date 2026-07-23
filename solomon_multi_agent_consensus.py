"""
Solomon Perpetual Learning Machine
Phase 19: Collaborative Multi-Agent Consensus Protocol

Orchestrates multi-agent voting protocols over proposed actions, skills, or model swaps,
requiring a strict weighted consensus threshold of >75% before deployment.
"""

import time
from typing import Dict, List, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class MultiAgentConsensus:
    """
    Manages voting structures and consensus thresholds across active system agents.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db
        # Static agent voter weights matching prerequisite capabilities
        self.agent_weights = {
            "Gabriel": 1.5,
            "Mnemosyne": 1.2,
            "Prometheus": 1.0,
            "Loki": 0.8
        }

    def evaluate_action_proposal(
        self,
        proposal_id: str,
        description: str,
        votes: Dict[str, bool] # AgentName -> True (Approve) / False (Reject)
    ) -> Dict[str, Any]:
        """
        Gathers votes, calculates weight ratios, and assesses consensus thresholds (>75%).
        """
        total_weight = sum(self.agent_weights.values())
        approving_weight = 0.0

        for agent, approved in votes.items():
            if agent in self.agent_weights:
                if approved:
                    approving_weight += self.agent_weights[agent]

        consensus_ratio = approving_weight / total_weight if total_weight > 0 else 0.0
        consensus_ratio = float(round(consensus_ratio, 4))

        consensus_threshold = 0.75
        consensus_reached = consensus_ratio >= consensus_threshold

        # Log outcome
        status = "CONSENSUS_REACHED" if consensus_reached else "CONSENSUS_FAILED"
        message = (
            f"Consensus evaluation complete for proposal '{proposal_id}'. "
            f"Approval weight is {consensus_ratio*100:.1f}% ({approving_weight}/{total_weight}). "
            f"{'Approved' if consensus_reached else 'Rejected'}."
        )

        # Persist consensus card to SQLite database
        card_id = f"SOK-CONSENSUS-{proposal_id.upper().replace('-', '_')}"
        content = (
            f"MULTI-AGENT CONSENSUS PROTOCOL: {proposal_id}\n"
            f"Description: {description}\n"
            f"Votes Gathered: {votes}\n"
            f"Consensus Score: {consensus_ratio*100:.1f}% (Required: {consensus_threshold*100:.1f}%)\n"
            f"Outcome: {status}\n"
            f"Details: {message}"
        )
        focus = "Validated multi-agent consensus protocol"
        self.db.upsert_card(
            card_id=card_id,
            family="Execution",
            focus=focus,
            content=content,
            status="ACTIVE" if consensus_reached else "DRAFT"
        )
        self.db.update_card_status(card_id, "ACTIVE" if consensus_reached else "DRAFT")

        return {
            "status": "success",
            "proposal_id": proposal_id,
            "consensus_reached": consensus_reached,
            "approval_percentage": round(consensus_ratio * 100.0, 2),
            "required_percentage": consensus_threshold * 100.0,
            "approving_weight": approving_weight,
            "total_voter_weight": total_weight,
            "votes_cast": votes,
            "outcome_message": message,
            "db_persisted_id": card_id,
            "recommended_next_step": (
                "RECOMMENDED NEXT STEP:\n"
                "<span style='color: #00E676; font-weight: bold; font-size: 1.25em;'>"
                "If consensus was reached, formally proceed to execute the action or "
                "hot-swap active configs dynamically!</span>"
            )
        }
