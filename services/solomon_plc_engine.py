import datetime
import uuid
from typing import Dict, Any, Optional, List

from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.api.repository import CardRepository
from services.solomon_learning_writeback import LearningWriteback
from services.solomon_governance_approval_packet import GovernanceApprovalLane

class PerpetualLearningEngine:
    """Orchestrates the Perpetual Learning Cycle (PLC)."""

    def __init__(self, db_manager: DatabaseManager, embedder: Any, gov_log_file: str):
        self.db = db_manager
        self.repo = CardRepository(db_manager=db_manager, embedder=embedder)
        self.writeback = LearningWriteback(db_manager=db_manager)
        self.governance = GovernanceApprovalLane(log_file=gov_log_file)
        self.run_id = str(uuid.uuid4())[:8]

    def _execute(self, query: str, params: tuple) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute(query, params)
                conn.commit()
            finally:
                conn.close()

    def record_event(self, type: str, data: str) -> str:
        event_id = f"evt_{str(uuid.uuid4())[:8]}"
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        self._execute("INSERT INTO events (id, type, data, timestamp) VALUES (?, ?, ?, ?)",
                      (event_id, type, data, timestamp))
        return event_id

    def process_failure(self, task_id: str, event_id: str, lesson_content: str) -> Optional[str]:
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()

        # Candidate Generation and Deduplication
        res = self.writeback.record_lesson(packet_id="pkt_001", result="fail", memory="event", lesson=lesson_content)
        if not res["recorded"] and res.get("reason") == "duplicate":
            return None # Fast exit on duplicate

        candidate_id = f"cand_{str(uuid.uuid4())[:8]}"
        self._execute("INSERT INTO candidates (id, event_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (candidate_id, event_id, lesson_content, "pending_review", timestamp))

        # Governance Validation & Approval
        gov_packet = {"requires_approval": True, "approved_by": "Mark", "action": "approve_candidate", "timestamp": timestamp}
        gov_res = self.governance.review_packet(gov_packet)

        if gov_res["status"] == "approved":
            self._execute("INSERT INTO governance (id, candidate_id, status, approver, timestamp) VALUES (?, ?, ?, ?, ?)",
                          (f"gov_{str(uuid.uuid4())[:8]}", candidate_id, "approved", "Mark", timestamp))
            self._execute("UPDATE candidates SET status = ? WHERE id = ?", ("approved", candidate_id))

            # Active Memory Promotion
            card_id = f"card_{str(uuid.uuid4())[:8]}"
            card = KnowledgeCard(
                card_id=card_id,
                card_type="LESSON",
                schema_version="1.0",
                title="Firewall settings during API connect failure",
                summary="Check firewall settings when connection fails",
                body=lesson_content,
                status="ACTIVE",
                confidence=0.5,
                validation_state="VALID",
                created_at=timestamp,
                updated_at=timestamp,
                created_by="system",
                source_type="event",
                source_ids=[event_id],
                parent_card_ids=[],
                related_card_ids=[],
                tags=["firewall", "networking", "api"],
                security_classification="unclassified",
                evidence="Observed failure and recovered",
                why_created="To prevent future failures",
                problem_solved="Prevents hanging",
                future_work_dependent="None"
            )
            self.repo.create_card(card, creator="system", reason="Promoted candidate to active memory")

            self._execute("INSERT INTO memories (id, candidate_id, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                          (f"mem_{str(uuid.uuid4())[:8]}", candidate_id, lesson_content, "active", timestamp))
            return card_id
        return None

    def retrieve_memory(self, query: str) -> tuple[Optional[KnowledgeCard], List[Dict], float]:
        import time
        start_time = time.time()
        search_results = self.repo.search(query, card_type="LESSON")
        latency = time.time() - start_time

        if not search_results:
            return None, [], latency

        best_match = search_results[0]
        retrieved_card = KnowledgeCard.from_dict(best_match["card"])
        competing = [{"id": r["card_id"], "score": r["score"], "reason": r["explanation"]} for r in search_results[1:]]

        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        trace_id = f"trace_{str(uuid.uuid4())[:8]}"
        self._execute("INSERT INTO retrieval_traces (id, query, memory_id, timestamp) VALUES (?, ?, ?, ?)",
                      (trace_id, query, retrieved_card.card_id, timestamp))

        return retrieved_card, competing, latency

    def record_successful_use(self, task_id: str, retrieved_card: KnowledgeCard, score: float = 1.0) -> None:
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()

        retrieved_card.confidence = min(1.0, retrieved_card.confidence + 0.2)
        self.repo.update_card(retrieved_card, updater="system", reason="Successful task completion")

        use_id = f"use_{str(uuid.uuid4())[:8]}"
        trace_id = f"trace_{str(uuid.uuid4())[:8]}" # Mock trace link for now
        self._execute("INSERT INTO uses (id, trace_id, task_id, timestamp) VALUES (?, ?, ?, ?)",
                      (use_id, trace_id, task_id, timestamp))
        self._execute("INSERT INTO outcomes (id, use_id, score, timestamp) VALUES (?, ?, ?, ?)",
                      (f"out_{str(uuid.uuid4())[:8]}", use_id, score, timestamp))

    def create_checkpoint(self, data: str) -> str:
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        checkpoint_id = f"chk_{str(uuid.uuid4())[:8]}"
        self._execute("INSERT INTO checkpoints (id, data, timestamp) VALUES (?, ?, ?)",
                      (checkpoint_id, data, timestamp))
        return checkpoint_id

    def get_latest_checkpoint(self) -> Optional[Dict]:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, data, timestamp FROM checkpoints ORDER BY timestamp DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return {"id": row[0], "data": row[1], "timestamp": row[2]}
                return None
            finally:
                conn.close()
