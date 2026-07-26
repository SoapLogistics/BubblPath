from backend.core.reader import Reader

def test_conversation():
    reader = Reader()
    reader.add_conversation("context1", "continuation1")
    memory = reader.get_conversation_memory()
    assert "continuation1" in memory
