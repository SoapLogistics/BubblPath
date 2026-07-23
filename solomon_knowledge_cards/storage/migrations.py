# Migrations handling logic to add embedding column

def run_migrations(conn):
    cursor = conn.cursor()
    # Check if 'embedding' column exists
    cursor.execute("PRAGMA table_info(cards)")
    columns = [col[1] for col in cursor.fetchall()]

    if "embedding" not in columns:
        print("Running migration: Adding 'embedding' column to cards table.")
        cursor.execute("ALTER TABLE cards ADD COLUMN embedding TEXT")
        conn.commit()

# Call this from db.py's _initialize_db
