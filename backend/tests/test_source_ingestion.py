from backend.core.reader import Reader

def test_source_ingestion():
    reader = Reader()
    reader.ingest_source("source1")
    reader.ingest_source("source2")
    assert "source1" in reader.get_sources()
    assert "source2" in reader.get_sources()

def test_source_ingestion_failure():
    pass
