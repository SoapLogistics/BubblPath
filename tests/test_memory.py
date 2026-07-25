import pytest
import os
from solomon_memory.db_manager import DatabaseManager
from solomon_memory.models.schema import VFSModel, MemoryCardModel

@pytest.fixture(autouse=True)
def setup_teardown():
    # Use in-memory DB for tests
    db = DatabaseManager(":memory:")
    yield
    # No explicit teardown needed for in-memory SQLite per test run,
    # but we would normally drop tables or clear the singleton here.

def test_vfs_crud():
    filepath = "/test_vfs.txt"
    content = b"test data"

    VFSModel.write(filepath, content)
    assert VFSModel.read(filepath) == content

    assert filepath in VFSModel.list_files("/")

    assert VFSModel.delete(filepath) == True
    assert VFSModel.read(filepath) is None

def test_memory_card_crud():
    card_id = MemoryCardModel.create("semantic", "Test memory", {"source": "pytest"})
    assert card_id is not None

    card = MemoryCardModel.get(card_id)
    assert card is not None
    assert card['content'] == "Test memory"
    assert card['layer'] == "semantic"
    assert card['metadata']['source'] == "pytest"
    assert card['use_count'] == 0

    MemoryCardModel.increment_use(card_id)
    card = MemoryCardModel.get(card_id)
    assert card['use_count'] == 1
