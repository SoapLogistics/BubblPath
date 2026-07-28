import pytest
from backend.services.kac.reprocessing.reprocessing_engine import ReprocessingEngine

def test_reprocessing_evaluation():
    engine = ReprocessingEngine(current_parser_version="2.0", current_extraction_version="2.0")

    # Needs upgrade
    manifest = {"vault_id": "v1", "parser_version": "1.0", "extraction_version": "1.0"}
    job = engine.evaluate_vault(manifest)

    assert job["status"] == "QUEUED"
    assert job["priority"] in ["HIGH", "MEDIUM"]
    assert job["expected_yield_gain"] > 0

    # Does not need upgrade
    manifest_up_to_date = {"vault_id": "v2", "parser_version": "2.0", "extraction_version": "2.0"}
    job_skip = engine.evaluate_vault(manifest_up_to_date)

    assert job_skip["status"] == "SKIPPED"
