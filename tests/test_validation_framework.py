import os
import pytest
import time
import tempfile
from services.solomon_validation_framework import ValidationFrameworkEngine

def test_validation_framework_success():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        log_path = tmp.name

    try:
        engine = ValidationFrameworkEngine(log_path=log_path)

        # Initialize Job
        job_id = "test_job_001"
        res = engine.initialize_validation(job_id)
        assert res["status"] == "recorded"

        # Advance steps
        for i in range(len(engine.STEPS) - 1):
            res = engine.advance_step(job_id, i, engine.STATE_PASSED)
            assert res["status"] == "advanced"

        # Final step
        evidence = {
            "test_summaries": {"unit": 100},
            "coverage": 95,
            "performance": {"p99": 10},
            "resources": {"cpu": "1%"},
            "known_limitations": ["None"],
            "rollback_tested": True
        }
        res = engine.advance_step(job_id, len(engine.STEPS) - 1, engine.STATE_PASSED, evidence)

        assert res["status"] == "validation_complete"
        assert res["action"] == "promotion_recommended"
        assert res["evidence_package"]["job_id"] == job_id
        assert res["evidence_package"]["coverage_report"] == 95
    finally:
        os.remove(log_path)

def test_validation_framework_failure():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        log_path = tmp.name

    try:
        engine = ValidationFrameworkEngine(log_path=log_path)

        job_id = "test_job_002"
        res = engine.initialize_validation(job_id)
        assert res["status"] == "recorded"

        evidence = {"logs": "NullPointerException at line 42"}
        # Fail at unit tests (step index 2)
        res = engine.advance_step(job_id, 2, engine.STATE_FAILED, evidence)

        assert res["status"] == "validation_failed"
        assert res["failed_step"] == "Unit Tests"
        assert res["action"] == "blocked_promotion"
        assert "Mnemosyne" in res["integrations"]
        assert res["diagnostic_logs"] == "NullPointerException at line 42"
    finally:
        os.remove(log_path)
