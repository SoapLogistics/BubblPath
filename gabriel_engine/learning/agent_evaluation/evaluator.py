from typing import Dict, Any, List
from gabriel_engine.learning.models import AgentPerformanceProfile

class AgentEvaluator:
    """
    Evaluates agent performance based on ingested outcomes to update agent-performance profiles.
    """
    def update_profile(self, profile: AgentPerformanceProfile, outcome: Dict[str, Any]) -> AgentPerformanceProfile:
        """
        Updates an agent's performance profile based on a new outcome.
        """
        if outcome.get("success"):
            # Simplified update logic for the success rate
            profile.success_rate = min(1.0, profile.success_rate + 0.01)
        else:
            profile.success_rate = max(0.0, profile.success_rate - 0.02)
            profile.feedback_notes.append(f"Failed outcome ingested from {outcome.get('ingest_id')}")
        return profile
