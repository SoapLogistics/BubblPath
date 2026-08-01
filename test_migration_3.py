import sqlite3
import os
from solomon_knowledge_cards.storage.db import DatabaseManager

db_path = "test_lab.db"
if os.path.exists(db_path):
    os.remove(db_path)

db = DatabaseManager(db_path)
conn = db._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT MAX(version) FROM schema_version")
version = cursor.fetchone()[0]
print(f"Migration version: {version}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'lab_%';")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables: {tables}")
