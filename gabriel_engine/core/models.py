import datetime
from typing import List, Dict, Any, Optional

class AcquisitionRecord:
    def __init__(
        self,
        project_name: str,
        source_location: str,
        source_type: str,
        owner_authorization: str = "user_provided",
        license_detected: str = "Unknown",
        allowed_actions: Optional[List[str]] = None,
        prohibited_actions: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
        content_hash: str = "",
        aggressive_mode: bool = True
    ):
        self.project_name = project_name
        self.source_location = source_location
        self.source_type = source_type
        self.owner_authorization = owner_authorization
        self.license_detected = license_detected
        self.allowed_actions = allowed_actions or []
        self.prohibited_actions = prohibited_actions or []
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        self.content_hash = content_hash
        self.aggressive_mode = aggressive_mode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "source_location": self.source_location,
            "source_type": self.source_type,
            "owner_authorization": self.owner_authorization,
            "license_detected": self.license_detected,
            "allowed_actions": self.allowed_actions,
            "prohibited_actions": self.prohibited_actions,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
            "aggressive_mode": self.aggressive_mode
        }


class ProgramAnatomyCard:
    def __init__(
        self,
        capability: str,
        inputs: List[str],
        outputs: List[str],
        core_mechanisms: List[str],
        valuable_patterns: List[str],
        solomon_relevance: List[str],
        languages: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None
    ):
        self.capability = capability
        self.inputs = inputs
        self.outputs = outputs
        self.core_mechanisms = core_mechanisms
        self.valuable_patterns = valuable_patterns
        self.solomon_relevance = solomon_relevance
        self.languages = languages or []
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "core_mechanisms": self.core_mechanisms,
            "valuable_patterns": self.valuable_patterns,
            "solomon_relevance": self.solomon_relevance,
            "languages": self.languages,
            "dependencies": self.dependencies
        }


class CapabilityMemoryCard:
    def __init__(
        self,
        name: str,
        source_project: str,
        source_license: str,
        concept_summary: str,
        implementation_status: str = "independently_implemented",
        confidence: float = 1.0,
        tested_on: Optional[List[str]] = None,
        result: Optional[Dict[str, Any]] = None,
        card_type: str = "capability_pattern"
    ):
        self.card_type = card_type
        self.name = name
        self.source_project = source_project
        self.source_license = source_license
        self.concept_summary = concept_summary
        self.implementation_status = implementation_status
        self.confidence = confidence
        self.tested_on = tested_on or []
        self.result = result or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_type": self.card_type,
            "name": self.name,
            "source_project": self.source_project,
            "source_license": self.source_license,
            "concept_summary": self.concept_summary,
            "implementation_status": self.implementation_status,
            "confidence": self.confidence,
            "tested_on": self.tested_on,
            "result": self.result
        }


class CrucibleReport:
    def __init__(
        self,
        baseline_metrics: Dict[str, Any],
        capability_metrics: Dict[str, Any],
        comparison_results: Dict[str, Any],
        decision: str,
        notes: str = ""
    ):
        self.baseline_metrics = baseline_metrics
        self.capability_metrics = capability_metrics
        self.comparison_results = comparison_results
        self.decision = decision
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_metrics": self.baseline_metrics,
            "capability_metrics": self.capability_metrics,
            "comparison_results": self.comparison_results,
            "decision": self.decision,
            "notes": self.notes
        }

import sqlite3
import threading

class DatabaseManager:
    _instances = {}
    _lock = threading.RLock()

    def __new__(cls, db_path: str = "solomon_soss.db"):
        with cls._lock:
            if (cls, db_path) not in cls._instances:
                instance = super(DatabaseManager, cls).__new__(cls)
                instance._db_path = db_path
                # Keep memory connection alive
                instance._memory_conn = None
                if db_path == ":memory:":
                    instance._memory_conn = sqlite3.connect(db_path, check_same_thread=False)
                    instance._memory_conn.row_factory = sqlite3.Row
                    instance._memory_conn.execute("PRAGMA foreign_keys = ON;")
                cls._instances[(cls, db_path)] = instance
                instance._init_db()
            return cls._instances[(cls, db_path)]

    def backup_database(self, backup_path: str):
        if self._db_path == ":memory:":
            return
        import shutil
        import os
        if os.path.exists(self._db_path):
            shutil.copy2(self._db_path, backup_path)

    def _init_db(self):

        conn = self.get_connection()
        try:
            if self._db_path != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout = 10000;")
            # Set up version table for migrations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
            """)
            conn.commit()

            # Integrity check
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            if result != "ok":
                raise sqlite3.DatabaseError(f"Integrity check failed: {result}")
        finally:
            if self._db_path != ":memory:":
                conn.close()

    def get_connection(self) -> sqlite3.Connection:
        if self._db_path == ":memory:" and self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 10000;")
        return conn