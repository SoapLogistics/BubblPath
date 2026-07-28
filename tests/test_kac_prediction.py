import pytest
import os
from backend.services.kac.prediction.signal_detector import SignalDetector
from backend.services.kac.prediction.forward_test import PredictionLedger
from backend.services.kac.prediction.model_card import PredictiveModelCard

def test_signal_detector():
    sd = SignalDetector()
    extracted = [
        {"type": "prediction", "statement": "High queue depth leads to latency"}
    ]

    models = sd.build_candidates(extracted)
    assert len(models) == 1
    assert isinstance(models[0], PredictiveModelCard)
    assert models[0].causal_classification == "causal"

def test_prediction_ledger(tmp_path):
    storage = tmp_path / "ledger.json"
    ledger = PredictionLedger(storage_path=str(storage))

    pred_id = ledger.record_prediction(
        model_id="model123",
        target="latency",
        predicted_value="high",
        confidence=0.8,
        horizon="1 hour"
    )

    assert pred_id in ledger.ledger
    assert ledger.ledger[pred_id]["status"] == "PENDING"

    ledger.resolve_prediction(pred_id, actual_outcome="high", score=1.0)

    assert ledger.ledger[pred_id]["status"] == "RESOLVED"
    assert ledger.ledger[pred_id]["score"] == 1.0

    with pytest.raises(ValueError):
        ledger.resolve_prediction(pred_id, actual_outcome="low", score=0.0)
