from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClipboardItem(BaseModel):
    id: str
    content_type: str # 'markdown', 'code', 'terminal', 'patch', 'text'
    content: str
    timestamp: datetime
    project_id: Optional[str] = None
    is_favorite: bool = False

class SharedClipboard(BaseModel):
    items: List[ClipboardItem] = []

    def add_item(self, item: ClipboardItem):
        self.items.append(item)
