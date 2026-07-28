import pytest
from backend.services.kac.algorithms.candidate_detector import CandidateDetector
from backend.services.kac.algorithms.sandbox_runner import SandboxRunner
from backend.services.kac.algorithms.algorithm_card import AlgorithmCard

def test_candidate_detector():
    cd = CandidateDetector()
    extracted = [
        {"type": "algorithm", "description": "Assuming x > 0, do binary search", "knowledge_value": 0.8}
    ]

    cards = cd.detect_and_reconstruct(extracted)

    assert len(cards) == 1
    assert isinstance(cards[0], AlgorithmCard)
    assert len(cards[0].assumptions) > 0
    assert cards[0].confidence == 0.8

def test_sandbox_runner():
    runner = SandboxRunner()

    # Safe code
    res = runner.run_test("print('Hello World')")
    assert res["status"] == "success"
    assert "STATIC ANALYSIS ONLY" in res["output"]

    # Error code
    res = runner.run_test("1 %")
    assert res["status"] == "failed"
    assert "SyntaxError" in res["error"]

    # Security code
    res = runner.run_test("import os")
    assert res["status"] == "failed"
    assert "disabled" in res["error"]
