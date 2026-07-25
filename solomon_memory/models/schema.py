from typing import Optional, List
import json
import sqlite3
from solomon_memory.db_manager import DatabaseManager

class VFSModel:
    """Virtual File System Data Access Object"""

    @staticmethod
    def write(filepath: str, content: bytes, mime_type: str = "text/plain") -> None:
        db = DatabaseManager()
        query = """
            INSERT INTO vfs_files (filepath, content, mime_type, size, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(filepath) DO UPDATE SET
                content = excluded.content,
                mime_type = excluded.mime_type,
                size = excluded.size,
                updated_at = CURRENT_TIMESTAMP
        """
        db.execute_write(query, (filepath, content, mime_type, len(content)))

    @staticmethod
    def read(filepath: str) -> Optional[bytes]:
        db = DatabaseManager()
        rows = db.execute_query("SELECT content FROM vfs_files WHERE filepath = ?", (filepath,))
        if rows:
            return rows[0]['content']
        return None

    @staticmethod
    def delete(filepath: str) -> bool:
        db = DatabaseManager()
        # Custom logic needed here since execute_write doesn't return affected rows easily in our wrapper.
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("DELETE FROM vfs_files WHERE filepath = ?", (filepath,))
        rows_deleted = cursor.rowcount
        conn.commit()
        return rows_deleted > 0

    @staticmethod
    def list_files(prefix: str = "") -> List[str]:
        db = DatabaseManager()
        query = "SELECT filepath FROM vfs_files WHERE filepath LIKE ?"
        rows = db.execute_query(query, (f"{prefix}%",))
        return [row['filepath'] for row in rows]

class MemoryCardModel:
    """Data Access Object for Memory Cards"""

    @staticmethod
    def create(layer: str, content: str, metadata: dict = None) -> int:
        db = DatabaseManager()
        query = """
            INSERT INTO memory_cards (layer, content, metadata)
            VALUES (?, ?, ?)
        """
        meta_str = json.dumps(metadata) if metadata else "{}"
        return db.execute_write(query, (layer, content, meta_str))

    @staticmethod
    def get(card_id: int) -> Optional[dict]:
        db = DatabaseManager()
        query = "SELECT * FROM memory_cards WHERE id = ?"
        rows = db.execute_query(query, (card_id,))
        if rows:
            row = dict(rows[0])
            row['metadata'] = json.loads(row['metadata']) if row['metadata'] else {}
            return row
        return None

    @staticmethod
    def increment_use(card_id: int) -> None:
        db = DatabaseManager()
        query = "UPDATE memory_cards SET use_count = use_count + 1, last_accessed = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_write(query, (card_id,))
