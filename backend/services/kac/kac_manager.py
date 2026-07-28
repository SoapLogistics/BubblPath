import os
import json
import uuid
import hashlib
import time
from typing import Dict, List, Optional, Any
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

class KACManager:
    """
    Knowledge Assimilation Center Manager.
    Handles the queueing and processing jobs for incoming knowledge files.
    """
    def __init__(self, storage_dir: str = "kac_storage", db_file: str = "kac_queue.json"):
        self.storage_dir = storage_dir
        self.db_file = db_file
        self.queue: Dict[str, dict] = {}
        self.stats: Dict[str, Any] = {
            "books_processed": 0,
            "books_archived": 0,
            "knowledge_cards_created": 0,
            "memory_atoms_created": 0,
            "algorithms_extracted": 0,
            "prediction_models_generated": 0,
            "cross_domain_connections": 0,
            "knowledge_yield": 0.0,
            "average_assimilation_time": 0.0,
            "vault_capacity": 0.0
        }

        os.makedirs(self.storage_dir, exist_ok=True)
        self._load_queue()

    def _load_queue(self) -> None:
        """Loads persistent queue from disk."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
                    self.queue = data.get("queue", {})
                    # Ensure all stats keys exist to prevent KeyErrors on upgrade
                    loaded_stats = data.get("stats", {})
                    for k, v in loaded_stats.items():
                        self.stats[k] = v
            except json.JSONDecodeError:
                self.queue = {}

    def _save_queue(self) -> None:
        """Saves current queue to disk."""
        # Atomic write to prevent corruption
        temp_file = self.db_file + ".tmp"
        with open(temp_file, "w") as f:
            json.dump({"queue": self.queue, "stats": self.stats}, f, indent=4)
        os.replace(temp_file, self.db_file)

    def _get_file_hash(self, file: FileStorage) -> str:
        hasher = hashlib.sha256()
        file.seek(0)
        while True:
            chunk = file.read(4096)
            if not chunk:
                break
            hasher.update(chunk)
        file.seek(0)
        return hasher.hexdigest()

    def ingest_file(self, file: FileStorage, priority: str = "Normal") -> dict:
        """Ingests a file, checking for duplicates, and adds to queue."""
        if not file or not file.filename:
            raise ValueError("Invalid file object provided.")

        filename = secure_filename(file.filename)
        file_hash = self._get_file_hash(file)

        # Check for duplicates based on file hash
        for job_id, job in self.queue.items():
            if job.get("file_hash") == file_hash:
                raise ValueError(f"Duplicate file detected. Already in queue as job {job_id}.")

        job_id = str(uuid.uuid4())
        save_path = os.path.join(self.storage_dir, f"{job_id}_{filename}")
        file.save(save_path)

        # Determine destination vault logically
        ext = os.path.splitext(filename)[1].lower()
        topic = "General Knowledge"
        if ext in ['.py', '.js', '.json', '.rs', '.go', '.ts', '.c', '.cpp']:
            topic = "Programming Foundations"

        vault_name = f"{topic} Vault 001"

        job = {
            "id": job_id,
            "filename": filename,
            "status": "Waiting",
            "priority": priority,
            "pages": 0, # Estimated
            "estimated_tokens": 0,
            "estimated_time": "TBD",
            "destination_vault": vault_name,
            "current_stage": "Waiting",
            "file_hash": file_hash,
            "filepath": save_path,
            "added_at": time.time()
        }

        self.queue[job_id] = job
        self._save_queue()

        return job

    def get_queue(self) -> List[dict]:
        """Returns the queue as a list sorted by time."""
        return sorted(list(self.queue.values()), key=lambda x: x.get("added_at", 0))

    def get_stats(self) -> dict:
        """Returns system metrics."""
        return self.stats

    def process_next_job(self) -> None:
        """
        Simulates the background processing of a job through the pipeline.
        In a real scenario, this would be handled by a Celery worker or similar.
        """
        from .parser.parser_manager import ParserManager
        from .extraction.extraction_engine import ExtractionEngine
        from .algorithms.candidate_detector import CandidateDetector
        from .prediction.signal_detector import SignalDetector

        # Find next waiting job
        for job_id, job in self.queue.items():
            if job["status"] == "Waiting":
                job["status"] = "Parsing"
                self._save_queue()

                try:
                    # 1. Parse Document (Mission 2)
                    pm = ParserManager()
                    canonical_doc = pm.process_file(job["filepath"], job["file_hash"])

                    job["status"] = "Extracting"
                    self._save_queue()

                    # 2. Extract Intelligence (Mission 3)
                    ee = ExtractionEngine()
                    intelligence = ee.extract_intelligence(canonical_doc)

                    # 3. Algorithm Discovery (Mission 4)
                    job["status"] = "Algorithm Discovery"
                    self._save_queue()
                    cd = CandidateDetector()
                    algorithm_cards = cd.detect_and_reconstruct(intelligence.get("algorithms", []))

                    # 4. Prediction Discovery (Mission 5)
                    job["status"] = "Prediction Modeling"
                    self._save_queue()
                    sd = SignalDetector()
                    predictive_models = sd.build_candidates(intelligence.get("predictions", []))

                    # Update Stats
                    self.stats["books_processed"] += 1
                    self.stats["knowledge_cards_created"] += len(intelligence["facts"]) + len(intelligence["concepts"])
                    self.stats["algorithms_extracted"] += len(algorithm_cards)
                    self.stats["prediction_models_generated"] += len(predictive_models)
                    self.stats["memory_atoms_created"] += len(intelligence["facts"]) * 2 # rough estimate

                    job["status"] = "Completed"
                    job["extracted_artifacts"] = {
                        "facts": len(intelligence["facts"]),
                        "concepts": len(intelligence["concepts"]),
                        "algorithms": len(algorithm_cards),
                        "predictions": len(predictive_models)
                    }
                    self._save_queue()
                except Exception as e:
                    job["status"] = "Failed"
                    job["error"] = str(e)
                    self._save_queue()
                break # Process one job per call
