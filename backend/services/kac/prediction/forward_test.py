import json
import os
import uuid
import time
from typing import Dict, Any

class PredictionLedger:
    """
    Immutable ledger of forward predictions.
    Records predictions before outcomes are known.
    """
    def __init__(self, storage_path="kac_prediction_ledger.json"):
        self.storage_path = storage_path
        self.ledger: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.ledger = json.load(f)

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.ledger, f, indent=4)

    def record_prediction(self, model_id: str, target: str, predicted_value: Any, confidence: float, horizon: str) -> str:
        pred_id = str(uuid.uuid4())
        self.ledger[pred_id] = {
            "prediction_id": pred_id,
            "model_id": model_id,
            "target": target,
            "predicted_value": predicted_value,
            "confidence": confidence,
            "horizon": horizon,
            "status": "PENDING",
            "created_at": time.time(),
            "resolved_at": None,
            "outcome": None,
            "score": None
        }
        self._save()
        return pred_id

    def resolve_prediction(self, prediction_id: str, actual_outcome: Any, score: float):
        if prediction_id not in self.ledger:
            raise ValueError("Prediction ID not found")

        pred = self.ledger[prediction_id]
        if pred["status"] != "PENDING":
            raise ValueError("Prediction is already resolved")

        pred["status"] = "RESOLVED"
        pred["resolved_at"] = time.time()
        pred["outcome"] = actual_outcome
        pred["score"] = score
        self._save()
