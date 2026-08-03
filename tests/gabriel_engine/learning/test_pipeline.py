from gabriel_engine.learning.pipeline import LearningPipeline

def test_learning_pipeline_evidence_flow():
    pipeline = LearningPipeline()

    # Ingest dummy data
    pipeline.ingestor.ingest("project_assimilation", {"success": True, "event_type": "project_assimilation", "actors": ["jules"]})
    pipeline.ingestor.ingest("mission", {"success": False, "event_type": "mission", "actors": ["claude"]})

    assert len(pipeline.ingestor.get_pending_outcomes()) == 2

    results = pipeline.run_cycle()

    assert results["ingested_count"] == 2
    assert results["evidence_extracted"] == 2
    assert results["learning_records_created"] == 2
    assert results["records_validated"] == 1 # The successful one

    assert len(pipeline.ingestor.get_pending_outcomes()) == 0
    assert len(pipeline.learning_records) == 2

def test_learning_pipeline_evolution():
    pipeline = LearningPipeline()

    # 1. First cycle: create a PENDING record from a failure
    pipeline.ingestor.ingest("mission", {"success": False, "event_type": "mission_alpha"})
    res1 = pipeline.run_cycle()
    assert res1["learning_records_created"] == 1

    record_id = list(pipeline.learning_records.keys())[0]
    record = pipeline.learning_records[record_id]
    assert record.validation_status == "PENDING"
    assert record.confidence == 0.3

    # 2. Second cycle: evolve it with a success
    pipeline.ingestor.ingest("mission", {"success": True, "event_type": "mission_alpha"})
    res2 = pipeline.run_cycle()
    assert res2["records_evolved"] == 1

    record = pipeline.learning_records[record_id]
    assert record.validation_status == "PENDING"
    assert round(record.confidence, 1) == 0.4
    assert len(record.supporting_missions) == 1
    assert len(record.contradicting_missions) == 1
    assert len(record.evidence) == 2

    # 3. Third cycle: evolve it with multiple successes to hit validation threshold
    for _ in range(4):
        pipeline.ingestor.ingest("mission", {"success": True, "event_type": "mission_alpha"})
    res3 = pipeline.run_cycle()

    assert res3["records_evolved"] == 4
    assert res3["records_validated"] == 1

    record = pipeline.learning_records[record_id]
    assert record.validation_status == "VALIDATED"
    assert record.confidence >= 0.8
