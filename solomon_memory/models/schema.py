import logging
from solomon_memory.db_manager import DatabaseManager

logger = logging.getLogger("MnemosyneSchema")

def initialize_schema():
    db = DatabaseManager()
    schema = """
    CREATE TABLE IF NOT EXISTS sok_cards (
        card_id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        embedding_cluster INTEGER DEFAULT 0,
        ttl_expires_at INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sok_edges (
        source_id TEXT,
        target_id TEXT,
        edge_weight REAL DEFAULT 1.0,
        semantic_type TEXT,
        FOREIGN KEY(source_id) REFERENCES sok_cards(card_id),
        FOREIGN KEY(target_id) REFERENCES sok_cards(card_id),
        PRIMARY KEY(source_id, target_id, semantic_type)
    );
    """
    try:
        with db.get_cursor() as cursor:
            cursor.executescript(schema)
        logger.info("Mnemosyne advanced SOK schema initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
