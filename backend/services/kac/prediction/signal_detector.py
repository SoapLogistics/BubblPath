from typing import List, Dict, Any
from .model_card import PredictiveModelCard
import uuid

class SignalDetector:
    """
    Detects predictive claims from extracted predictions and creates Candidate Predictive Model Cards.
    """
    def build_candidates(self, extracted_predictions: List[Dict[str, Any]]) -> List[PredictiveModelCard]:
        models = []
        for ext in extracted_predictions:
            statement = ext.get('statement', '')

            # Very naive heuristic
            causal = "correlational"
            if "cause" in statement.lower() or "leads to" in statement.lower():
                causal = "causal"

            model = PredictiveModelCard(
                model_id=str(uuid.uuid4()),
                name="Discovered Predictive Model",
                target="Extracted Target",
                inputs=[],
                conditions=[],
                horizon="Unknown",
                model_form=statement,
                causal_classification=causal,
                baseline="historical average",
                provenance=ext.get('source', {})
            )
            models.append(model)

        return models
