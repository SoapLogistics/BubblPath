import sqlite3
import json
import threading
from typing import List, Optional
from contextlib import closing

from .models import ContradictionCase, Claim, ContradictionEvidence, ResolutionProposal, ClaimScope

class ContradictionRepository:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if hasattr(self, '_mem_conn') and self.db_path == ":memory:":
            return self._mem_conn

        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Optimizations for concurrency and reliability
        conn.execute("PRAGMA foreign_keys = ON;")
        if self.db_path != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self):
        # We must keep connection open when using :memory: across methods,
        # but since we use short-lived connections per method we'll implement shared connection caching for :memory:.
        # For simplicity, if db_path is :memory:, sqlite3 drops it upon close.
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row

        with self._lock:
            conn = self._get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contradiction_cases (
                    id TEXT PRIMARY KEY,
                    classification TEXT NOT NULL,
                    severity REAL NOT NULL,
                    priority_score REAL NOT NULL,
                    evidence_json TEXT NOT NULL,
                    proposals_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()

    def save_case(self, case: ContradictionCase) -> None:
        """Saves or updates a contradiction case. Duplicate cases are naturally handled by the primary key."""
        with self._lock:
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO contradiction_cases
                (id, classification, severity, priority_score, evidence_json, proposals_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    classification = excluded.classification,
                    severity = excluded.severity,
                    priority_score = excluded.priority_score,
                    evidence_json = excluded.evidence_json,
                    proposals_json = excluded.proposals_json,
                    status = excluded.status,
                    updated_at = excluded.updated_at
            """, (
                case.id,
                case.classification,
                case.severity,
                case.priority_score,
                json.dumps(case.evidence.to_dict()),
                json.dumps([p.to_dict() for p in case.proposals]),
                case.status,
                case.created_at,
                case.updated_at
            ))
            conn.commit()
            if self.db_path != ":memory:":
                conn.close()

    def get_case(self, case_id: str) -> Optional[ContradictionCase]:
        with self._lock:
            conn = self._get_connection()
            row = conn.execute("SELECT * FROM contradiction_cases WHERE id = ?", (case_id,)).fetchone()
            if self.db_path != ":memory:":
                conn.close()
            if not row:
                return None
            return self._row_to_case(row)

    def list_cases(self, status: Optional[str] = None) -> List[ContradictionCase]:
        with self._lock:
            conn = self._get_connection()
            if status:
                rows = conn.execute("SELECT * FROM contradiction_cases WHERE status = ? ORDER BY priority_score DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM contradiction_cases ORDER BY priority_score DESC").fetchall()
            if self.db_path != ":memory:":
                conn.close()
            return [self._row_to_case(row) for row in rows]

    def _dict_to_claim(self, d: dict) -> Claim:
        scope_dict = d.pop('scope', {})
        scope = ClaimScope(**scope_dict)
        d['scope'] = scope
        return Claim(**d)

    def _row_to_case(self, row: sqlite3.Row) -> ContradictionCase:
        evidence_dict = json.loads(row['evidence_json'])
        claim_a = self._dict_to_claim(evidence_dict['claim_a'])
        claim_b = self._dict_to_claim(evidence_dict['claim_b'])

        proposals_list = json.loads(row['proposals_json'])
        proposals = [ResolutionProposal(**p) for p in proposals_list]

        return ContradictionCase(
            id=row['id'],
            classification=row['classification'],
            severity=row['severity'],
            priority_score=row['priority_score'],
            evidence=ContradictionEvidence(claim_a=claim_a, claim_b=claim_b),
            proposals=proposals,
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
