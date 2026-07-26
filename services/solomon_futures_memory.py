import sqlite3
import json
import uuid
import time
from typing import Dict, Any

route_key = "futures_memory_outbox"

class FuturesMemoryOutbox:
    def __init__(self, db_path="solomon_soss.db"):
        self.db_path = db_path
        self._init_outbox()

    def _init_outbox(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS futures_memory_outbox (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    payload_json TEXT,
                    status TEXT,
                    attempts INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)

    def queue_event(self, event_type: str, payload: Dict[str, Any]):
        """Durable outbox for memory delivery."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO futures_memory_outbox (id, event_type, payload_json, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), event_type, json.dumps(payload), "PENDING", str(time.time()))
            )

class FuturesOutcomeReconciler:
    def __init__(self, db_path="solomon_soss.db"):
        self.db_path = db_path
        self.outbox = FuturesMemoryOutbox(db_path)
        self._init_outcomes()

    def _init_outcomes(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS futures_outcomes (
                    candidate_id TEXT PRIMARY KEY,
                    actual_outcome INTEGER,
                    source TEXT,
                    verified_at TEXT
                )
            """)

    def reconcile_outcome(self, candidate_id: str, actual_outcome: bool, source: str):
        """
        Ingests a verified real-world outcome, reconciles it against the run, and triggers memory learning securely.
        """
        outcome_val = 1 if actual_outcome else 0
        timestamp = str(time.time())

        with sqlite3.connect(self.db_path) as conn:
            # Save the immutable outcome
            conn.execute(
                "INSERT OR IGNORE INTO futures_outcomes (candidate_id, actual_outcome, source, verified_at) VALUES (?, ?, ?, ?)",
                (candidate_id, outcome_val, source, timestamp)
            )

            # Fetch the associated simulation run to evaluate learning
            cur = conn.cursor()
            cur.execute("SELECT status, simulation_probability FROM futures_simulation_runs WHERE candidate_id = ?", (candidate_id,))
            run = cur.fetchone()

            if run:
                status, prob = run
                # Example rule: Only write a confirmed lesson pattern if we confidently missed
                if status == "CONFIRMED_90_PLUS" and not actual_outcome:
                    self.outbox.queue_event("failure_pattern", {
                        "candidate_id": candidate_id,
                        "expected_probability": prob,
                        "actual": False,
                        "reason": "Calibration miss on 90+ threshold"
                    })
                elif status == "CONFIRMED_90_PLUS" and actual_outcome:
                    self.outbox.queue_event("lesson_memory", {
                        "candidate_id": candidate_id,
                        "expected_probability": prob,
                        "actual": True,
                        "reason": "Successful 90+ realization"
                    })
