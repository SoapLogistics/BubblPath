from backend.core.reader import Reader

def test_workspace():
    reader = Reader()
    workspace = reader.activate_workspace("123")
    assert workspace["active"] is True
