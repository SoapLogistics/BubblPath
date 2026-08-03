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
