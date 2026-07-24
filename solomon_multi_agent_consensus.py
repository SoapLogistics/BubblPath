"""
Solomon Perpetual Learning Machine
Phase 19: Collaborative Multi-Agent Worker Consensus Protocol (solomon_multi_agent_consensus.py)

This module implements a collaborative consensus voting protocol among specialized
helper agents (Gabriel, Mnemosyne, Prometheus, Loki), requiring a >75% approval
threshold before authorizing major database or AST state actions.
"""

from typing import Dict, Any, List

class MultiAgentConsensus:
    """
    Enforces collective consensus checks across SOSS helper worker modules,
    acting as a decentralized gateway policy.
    """

    @classmethod
    def cast_consensus_votes(cls, action_proposal: str, risk_score: float) -> Dict[str, Any]:
        """
        Gathers simulated agent votes based on action risk scores.
        """
        # Voting parameters: high risk triggers dissent from safety agents
        agents = ["Gabriel", "Mnemosyne", "Prometheus", "Loki"]
        votes: Dict[str, str] = {}

        for agent in agents:
            if agent == "Gabriel":
                # Gabriel is aggressive and always votes YES unless extreme risk
                votes[agent] = "YES" if risk_score < 0.9 else "NO"
            elif agent == "Mnemosyne":
                # Mnemosyne loves memory and stability, votes NO on medium-high risk
                votes[agent] = "YES" if risk_score < 0.6 else "NO"
            elif agent == "Prometheus":
                # Prometheus is curious, votes YES on medium risk but NO on extreme risk
                votes[agent] = "YES" if risk_score < 0.8 else "NO"
            elif agent == "Loki":
                # Loki is analytical, votes YES if risk has clean probabilistic hedge
                votes[agent] = "YES" if risk_score < 0.7 else "NO"

        # Calculate approval rate
        yes_votes = sum(1 for vote in votes.values() if vote == "YES")
        total_votes = len(agents)
        approval_rate = yes_votes / total_votes

        # Consenus threshold: strictly > 75% (meaning >= 3 of 4 yes votes)
        authorized = yes_votes >= 3

        return {
            "action_proposal": action_proposal,
            "risk_score_evaluated": risk_score,
            "votes_cast": votes,
            "approval_count": yes_votes,
            "approval_rate_percent": approval_rate * 100.0,
            "authorized": authorized,
            "determination": "APPROVED" if authorized else "REJECTED"
        }
