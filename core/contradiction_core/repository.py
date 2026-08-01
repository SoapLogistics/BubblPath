import sqlite3
import json
import threading
from typing import List, Optional
from .models import ContradictionCase

class ContradictionRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 10000;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS contradiction_cases (
                            case_id TEXT PRIMARY KEY,
                            fingerprint TEXT NOT NULL UNIQUE,
                            classification TEXT NOT NULL,
                            severity REAL NOT NULL,
                            uncertainty REAL NOT NULL,
                            status TEXT NOT NULL,
                            serialized_data TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)

                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_cases_status ON contradiction_cases(status);
                    """)
            finally:
                conn.close()

    def store_case(self, case: ContradictionCase) -> None:
        case.validate()
        fingerprint = case.generate_fingerprint()
        serialized = json.dumps(case.to_dict())

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO contradiction_cases (
                        case_id, fingerprint, classification, severity,
                        uncertainty, status, serialized_data, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                        classification = excluded.classification,
                        severity = excluded.severity,
                        uncertainty = excluded.uncertainty,
                        status = excluded.status,
                        serialized_data = excluded.serialized_data,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    case.case_id, fingerprint, case.classification,
                    case.severity, case.uncertainty, case.status, serialized
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_case(self, case_id: str) -> Optional[ContradictionCase]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT serialized_data FROM contradiction_cases WHERE case_id = ?", (case_id,))
                row = cursor.fetchone()
                if row:
                    return ContradictionCase.from_dict(json.loads(row["serialized_data"]))
                return None
            finally:
                conn.close()

    def get_case_by_fingerprint(self, fingerprint: str) -> Optional[ContradictionCase]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT serialized_data FROM contradiction_cases WHERE fingerprint = ?", (fingerprint,))
                row = cursor.fetchone()
                if row:
                    return ContradictionCase.from_dict(json.loads(row["serialized_data"]))
                return None
            finally:
                conn.close()

    def list_cases(self, status: Optional[str] = None) -> List[ContradictionCase]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if status:
                    cursor.execute("SELECT serialized_data FROM contradiction_cases WHERE status = ?", (status,))
                else:
                    cursor.execute("SELECT serialized_data FROM contradiction_cases")

                return [ContradictionCase.from_dict(json.loads(row["serialized_data"])) for row in cursor.fetchall()]
            finally:
                conn.close()
