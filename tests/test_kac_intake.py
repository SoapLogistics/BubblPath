import pytest
import os
import json
from werkzeug.datastructures import FileStorage
from io import BytesIO
from backend.services.kac.kac_manager import KACManager

@pytest.fixture
def kac_manager(tmp_path):
    storage_dir = tmp_path / "kac_storage"
    db_file = tmp_path / "kac_queue.json"
    return KACManager(storage_dir=str(storage_dir), db_file=str(db_file))

def test_ingest_file(kac_manager):
    file_content = b"Dummy content for testing KAC intake"
    file = FileStorage(stream=BytesIO(file_content), filename="test_book.epub", content_type="application/epub+zip")

    job = kac_manager.ingest_file(file, priority="High")

    assert job["filename"] == "test_book.epub"
    assert job["status"] == "Waiting"
    assert job["priority"] == "High"
    assert "epub" in job["filepath"].lower()

    queue = kac_manager.get_queue()
    assert len(queue) == 1
    assert queue[0]["id"] == job["id"]

def test_duplicate_ingest(kac_manager):
    file_content = b"Same content"
    file1 = FileStorage(stream=BytesIO(file_content), filename="book1.epub")
    file2 = FileStorage(stream=BytesIO(file_content), filename="book2.pdf")

    kac_manager.ingest_file(file1)

    with pytest.raises(ValueError, match="Duplicate file detected"):
        kac_manager.ingest_file(file2)
