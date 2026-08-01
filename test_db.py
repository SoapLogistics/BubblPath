import sqlite3
from core.solomon_knowledge_cards.storage.db import DatabaseManager

db = DatabaseManager(":memory:")
print("DB initialized successfully")
