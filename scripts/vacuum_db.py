import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)

def vacuum_database(db_path: str):
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        logging.info(f"Vacuumed {db_path}")

if __name__ == "__main__":
    vacuum_database("solomon.db")
