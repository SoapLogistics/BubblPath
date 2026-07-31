import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models.project_room import ProjectRoom
from shared.models.clipboard import ClipboardItem, SharedClipboard

def test_project_room_model():
    room = ProjectRoom(
        id="test-1",
        name="Test Room",
        objective="Test the model",
        status="active"
    )
    assert room.id == "test-1"
    assert room.repositories == []

def test_clipboard_model():
    clipboard = SharedClipboard()
    item = ClipboardItem(
        id="item-1",
        content_type="text",
        content="Hello World",
        timestamp=datetime.now()
    )
    clipboard.add_item(item)
    assert len(clipboard.items) == 1
    assert clipboard.items[0].content == "Hello World"
