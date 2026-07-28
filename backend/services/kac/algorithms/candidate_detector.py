from typing import List, Dict, Any
from .algorithm_card import AlgorithmCard
import uuid

class CandidateDetector:
    """
    Detects algorithms from extracted knowledge fragments and reconstructs them into Algorithm Cards.
    """
    def detect_and_reconstruct(self, extracted_algorithms: List[Dict[str, Any]]) -> List[AlgorithmCard]:
        cards = []
        for ext in extracted_algorithms:
            # Reconstruct basic info
            desc = ext.get('description', '')

            # Simple assumption extraction
            assumptions = []
            if "assuming" in desc.lower():
                assumptions.append({"assumption": "extracted from text", "confidence": 0.5})

            card = AlgorithmCard(
                algorithm_id=str(uuid.uuid4()),
                name="Discovered Algorithm Candidate",
                family="Unknown",
                domain="General",
                problem_statement="Determined from context.",
                inputs=[],
                outputs=[],
                processing_steps=[desc],
                assumptions=assumptions,
                complexity={"time": "O(?)", "space": "O(?)"},
                pseudocode="TODO: Generate from extraction",
                confidence=ext.get('knowledge_value', 0.5),
                validation_status="UNVERIFIED",
                governance_status="PENDING",
                provenance=ext.get('source', {})
            )
            cards.append(card)

        return cards
