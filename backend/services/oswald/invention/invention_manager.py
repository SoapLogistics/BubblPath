from typing import List, Dict, Any
import uuid
from .invention_card import InventionCard
from .problem_registry import ProblemRecord
from backend.services.oswald.laboratory.hypothesis_manager import HypothesisCard

class InventionManager:
    """
    Synthesizes structural cross-domain concepts to generate Invention candidates.
    """
    def generate_candidate(self, problem: ProblemRecord, cross_domain_concepts: List[str]) -> InventionCard:
        """
        Combines a registered problem with structural concepts to propose a new method.
        """
        inv = InventionCard(
            invention_id=str(uuid.uuid4()),
            title=f"Novel Solution for {problem.title}",
            summary=f"Applies {', '.join(cross_domain_concepts[:2])} to resolve {problem.title}",
            problem_ids=[problem.problem_id],
            novelty_status="NEW_COMBINATION",
            proposed_method="Combine domains for optimized processing.",
            expected_benefit="Increased efficiency.",
            risk_level="MEDIUM"
        )
        return inv

    def convert_to_hypothesis(self, invention: InventionCard) -> HypothesisCard:
        """
        Converts a novel invention into a formal, testable Hypothesis for the Laboratory.
        """
        return HypothesisCard(
            hypothesis_id=str(uuid.uuid4()),
            problem=invention.summary,
            proposed_solution=invention.proposed_method,
            supporting_evidence=["Derived from cross-domain synthesis"],
            expected_improvement=invention.expected_benefit,
            subsystem=invention.title
        )
