import sqlite3

def check_db():
    try:
        from solomon_knowledge_cards.storage.db import DatabaseManager
        db = DatabaseManager('test_db_test.db')
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(cards)")
        cols = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {cols}")
    except Exception as e:
        print(f"Error: {e}")

check_db()
