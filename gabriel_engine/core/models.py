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
import datetime
import threading
import sqlite3
import shutil
import os
import time
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    _instance = None
    _init_lock = threading.Lock()

    def __new__(cls, db_path: str = "solomon_soss.db"):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._init_instance(db_path)
            return cls._instance

    def _init_instance(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # WAL mode
        conn.execute("PRAGMA busy_timeout = 10000;")  # 10 seconds busy timeout
        return conn

    def _backup_db(self):
        """Creates a backup before destructive operations or migrations."""
        if os.path.exists(self.db_path):
            backup_path = f"{self.db_path}.{int(time.time())}.bak"
            shutil.copy2(self.db_path, backup_path)

    def _init_db(self) -> None:
        """Runs migrations to initialize the schema."""
        with self._lock:
            self._backup_db()
            conn = self._get_connection()
            try:
                # Migration tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    );
                """)
                conn.commit()

                # Read current version
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_version")
                row = cursor.fetchone()
                current_version = row[0] if row[0] is not None else 0

                # Migration 1: Initial unified schema stub
                if current_version < 1:
                    with conn:
                        # Create tables based on data ownership matrix here if needed
                        conn.execute(
                            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                            (1, datetime.datetime.now(datetime.UTC).isoformat())
                        )

                # Integrity check after migration
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                if result[0] != "ok":
                    raise sqlite3.IntegrityError(f"Database integrity check failed: {result[0]}")
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def execute_read(self, query: str, parameters: Tuple = ()) -> List[sqlite3.Row]:
        """Executes a read query using parameterized SQL."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                return cursor.fetchall()
            finally:
                conn.close()

    def execute_write(self, query: str, parameters: Tuple = ()) -> None:
        """Executes a write query within a transaction boundary."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
