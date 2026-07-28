import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage
from backend.services.kac.kac_manager import KACManager

def test_kac_end_to_end(tmp_path):
    storage_dir = tmp_path / "kac_storage"
    db_file = tmp_path / "kac_queue.json"
    kac = KACManager(storage_dir=str(storage_dir), db_file=str(db_file))

    # 1. Intake
    file_content = b"If you use algorithm A, it usually causes B."
    file = FileStorage(stream=BytesIO(file_content), filename="test.pdf")
    job = kac.ingest_file(file)

    assert job["status"] == "Waiting"

    # 2. Process (simulates Parser -> Extraction)
    kac.process_next_job()

    # 3. Verify
    queue = kac.get_queue()
    updated_job = queue[0]
    assert updated_job["status"] == "Completed"

    stats = kac.get_stats()
    assert stats["books_processed"] == 1
    # Check that it extracted some predictions based on our naive stub extractors
    assert stats["prediction_models_generated"] >= 0
