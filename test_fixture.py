import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))
from solomon_knowledge_cards.storage.db import DatabaseManager

db_path = "test_fixture.db"
if os.path.exists(db_path):
    os.remove(db_path)

db = DatabaseManager(db_path)
conn = db._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print([r[0] for r in cursor.fetchall()])
