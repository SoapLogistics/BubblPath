import logging
import random
from typing import Dict, Any, List

logger = logging.getLogger("SPLE_Curiosity")

class CuriosityEngine:
    """
    Handles Part 4 of the SPLE blueprint: Curiosity.
    Drives autonomous exploration based on novelty, surprise, and information gain.
    """
    def __init__(self):
        self.frontier_map: List[str] = [] # Concepts we know we don't know
        self.world_model_predictions: Dict[str, Any] = {}
        logger.info("CuriosityEngine initialized.")

    def evaluate_surprise(self, event_context: str, actual_outcome: str, predicted_outcome: str) -> float:
        """
        Calculates prediction error (surprise). High surprise triggers curiosity.
        Simulates the Free Energy Principle.
        """
        # Simulated surprise calculation based on string mismatch length
        surprise_score = abs(len(actual_outcome) - len(predicted_outcome)) / max(len(actual_outcome), 1)
        # Normalize to 0.0 - 1.0
        surprise_score = min(surprise_score, 1.0)

        logger.info(f"Evaluated surprise for '{event_context[:20]}...': {surprise_score:.2f}")
        return surprise_score

    def generate_hypothesis(self, concept_gap: str) -> str:
        """
        Formulates a hypothesis to resolve a known gap in knowledge.
        """
        logger.info(f"Generating hypothesis for knowledge gap: {concept_gap}")
        return f"Hypothesis: The mechanism behind {concept_gap} involves hidden Markov interactions."

    def schedule_exploration(self) -> Dict[str, Any]:
        """
        Decides what to learn next based on intrinsic motivation.
        """
        if self.frontier_map:
            target = random.choice(self.frontier_map)
            logger.info(f"Scheduling exploration for frontier concept: {target}")
            return {"action": "explore", "target": target}
        else:
            logger.info("Frontier map empty. Engaging novelty search.")
            return {"action": "novelty_search", "domain": "random_arxiv_papers"}

    def add_to_frontier(self, concept: str):
        """Adds a concept to the list of known unknowns."""
        if concept not in self.frontier_map:
            self.frontier_map.append(concept)
            logger.info(f"Added '{concept}' to Knowledge Frontier Map.")
