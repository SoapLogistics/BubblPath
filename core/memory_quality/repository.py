import sqlite3
import json
from typing import List, Optional, Dict, Any
from core.memory_quality.models import MemoryQualityScore, QualityDimensions, ScoreExplanation
from core.solomon_knowledge_cards.storage.db import DatabaseManager

class MemoryQualityRepository:
    def __init__(self, db_manager: DatabaseManager = None):
        if db_manager is None:
            db_manager = DatabaseManager()
        self.db_manager = db_manager
        self._init_db()

    def _init_db(self):
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_quality_scores (
                        score_id TEXT PRIMARY KEY,
                        record_id TEXT,
                        policy_version TEXT,
                        timestamp TEXT,
                        final_score REAL,
                        features_snapshot TEXT,
                        explanation TEXT
                    )
                ''')
                conn.commit()
            finally:
                conn.close()

    def save_score(self, score: MemoryQualityScore):
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                conn.execute(
                    """
                    INSERT INTO memory_quality_scores
                    (score_id, record_id, policy_version, timestamp, final_score, features_snapshot, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        score.score_id,
                        score.record_id,
                        score.policy_version,
                        score.timestamp.isoformat(),
                        score.final_score,
                        score.features_snapshot.model_dump_json(),
                        score.explanation.model_dump_json()
                    )
                )
                conn.commit()
            finally:
                conn.close()

    def get_score(self, score_id: str) -> Optional[MemoryQualityScore]:
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                cursor = conn.execute(
                    "SELECT * FROM memory_quality_scores WHERE score_id = ?",
                    (score_id,)
                )
                row = cursor.fetchone()
                if row:
                    return self._row_to_score(row)
            finally:
                conn.close()
        return None

    def get_scores_for_record(self, record_id: str) -> List[MemoryQualityScore]:
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                cursor = conn.execute(
                    "SELECT * FROM memory_quality_scores WHERE record_id = ? ORDER BY timestamp DESC",
                    (record_id,)
                )
                rows = cursor.fetchall()
                return [self._row_to_score(row) for row in rows]
            finally:
                conn.close()

    def _row_to_score(self, row) -> MemoryQualityScore:
        import datetime
        return MemoryQualityScore(
            score_id=row['score_id'],
            record_id=row['record_id'],
            policy_version=row['policy_version'],
            timestamp=datetime.datetime.fromisoformat(row['timestamp']),
            final_score=row['final_score'],
            features_snapshot=QualityDimensions.model_validate_json(row['features_snapshot']),
            explanation=ScoreExplanation.model_validate_json(row['explanation'])
        )
