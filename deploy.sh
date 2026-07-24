#!/bin/bash
echo "Starting Deployment Protocol for Solomon Intelligence Engine..."

# Ensure we have the latest dependencies
pip install -r requirements.txt

# Run vacuum and optimization prep
python3 -c "
import sqlite3
import os
db_path = os.environ.get('SOLOMON_DB_PATH', 'solomon_mnemosyne.db')
conn = sqlite3.connect(db_path)
conn.execute('PRAGMA journal_mode=WAL;')
conn.execute('VACUUM;')
conn.close()
print('Database optimized.')
"

echo "Deployment prep complete. System is ready for gunicorn boot."
