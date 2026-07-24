import os
import json
import sqlite3
import hmac
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import DatabaseManager
from .embeddings import SemanticEmbedder

logger = logging.getLogger("mnemosyne_runtime")

CLEARANCE_ORDER = ["PUBLIC", "INTERNAL", "RESTRICTED"]

# Eleven SOK Card Families
CARD_FAMILIES = [
    "IDENTITY", "MISSION", "PROCEDURE", "TASK", "REVIEW",
    "KNOWLEDGE", "FAILURE", "REPAIR", "SKILL", "DECISION", "ARCHITECTURE"
]

def get_allowed_clearances(clearance: str) -> List[str]:
    c = (clearance or "INTERNAL").upper()
    if c not in CLEARANCE_ORDER:
        c = "INTERNAL"
    idx = CLEARANCE_ORDER.index(c)
    return CLEARANCE_ORDER[:idx + 1]

def get_dynamic_context_budget() -> int:
    """
    Dynamically calculates character-based context budget based on active SOLOMON_MODEL
    and available system RAM capacity headroom.
    """
    model = os.environ.get("SOLOMON_MODEL", "gpt-3.5-turbo").lower()
    # Default base budget
    budget = 4000

    if "gpt-4o" in model:
        budget = 64000
    elif "gpt-3.5" in model:
        budget = 16000
    elif "llama" in model or "local" in model:
        budget = 12000

    # Enforce memory headroom limits (scale down budget if RAM is tight)
    try:
        from .resource_monitor import get_memory_footprint_mb
        mem_mb = get_memory_footprint_mb()
        if mem_mb > 1200.0: # If process memory is near 1.5GB cap, compress budget to prevent OOM
            budget = min(budget, 6000)
    except Exception:
        pass

    return budget


class MnemosyneRuntime:
    """Project Mnemosyne high-priority long-term memory runtime engine."""
    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            db_path = os.environ.get(
                "SOLOMON_DB_PATH",
                "/srv/storage/toshiba/BubblePath/data/mnemosyne/solomon_mnemosyne.db"
            )
        # fallback to current directory if parent path is unwritable during local test
        try:
            db_dir = os.path.dirname(os.path.abspath(db_path))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        except Exception:
            db_path = "./solomon_mnemosyne.db"

        self.db_path = db_path
        self.db = DatabaseManager(self.db_path)
        self.embedder = SemanticEmbedder()

    def _update_card_embedding_in_db(self, card_id: str, embedding_json: str):
        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute("""
                    UPDATE knowledge_cards
                    SET embedding = ?
                    WHERE card_id = ?
                """, (embedding_json, card_id))
        except Exception as e:
            logger.error(f"Failed to cache embedding for card {card_id}: {str(e)}")
        finally:
            conn.close()

    def add_card_link(self, source_id: str, target_id: str, relationship_type: str) -> bool:
        """Establishes a relational link between two Knowledge Cards (DEPENDS_ON, PREVENTS, ENHANCES)."""
        rel_types = ["DEPENDS_ON", "PREVENTS", "ENHANCES", "PROPOSES_UPDATE_TO"]
        if relationship_type.upper() not in rel_types:
            raise ValueError(f"Invalid relationship type: {relationship_type}. Must be one of {rel_types}")

        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR IGNORE INTO card_links (source_id, target_id, relationship_type, created_at)
                    VALUES (?, ?, ?, ?);
                """, (source_id, target_id, relationship_type.upper(), datetime.utcnow().isoformat()))
            return True
        except Exception as e:
            logger.error(f"Failed to create card link from {source_id} to {target_id}: {str(e)}")
            return False
        finally:
            conn.close()

    def get_card_links(self, card_id: str) -> List[Dict[str, Any]]:
        """Retrieves all active relational links for a specific card."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("""
                SELECT * FROM card_links
                WHERE source_id = ? OR target_id = ?
            """, (card_id, card_id))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def add_execution_trace(self, request_id: str, conversation_id: str, step_name: str, details: Any):
        """Records a step in the execution path for real-time visual debugging traces."""
        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO execution_traces (request_id, conversation_id, step_name, details, timestamp)
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    request_id,
                    conversation_id,
                    step_name,
                    json.dumps(details) if not isinstance(details, str) else details,
                    datetime.utcnow().isoformat()
                ))
        except Exception as e:
            logger.error(f"Failed to record execution trace for {request_id}: {str(e)}")
        finally:
            conn.close()

    def retrieve_context(
        self,
        query: str,
        clearance: str,
        task_type: Optional[str] = None,
        procedure_ids: Optional[List[str]] = None,
        limit: int = 3,
        context_budget_chars: int = 4000  # Strict context budget to prevent prompt paralysis
    ) -> Dict[str, Any]:
        """
        Retrieves approved/active valid knowledge cards matching search query and clearance level.
        Enforces a maximum characters context budget to prevent prompt paralysis.
        """
        if context_budget_chars == 4000:
            context_budget_chars = get_dynamic_context_budget()

        allowed = get_allowed_clearances(clearance)
        placeholders = ",".join("?" for _ in allowed)

        conn = self.db.get_connection()
        try:
            sql = f"""
                SELECT * FROM knowledge_cards
                WHERE validation_state IN ('APPROVED', 'ACTIVE')
                  AND security_classification IN ({placeholders})
            """
            params = list(allowed)

            if task_type:
                sql += " AND card_type = ?"
                params.append(task_type.upper())

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            query_tokens = [t.lower() for t in query.split() if t]
            query_emb = self.embedder.get_embedding(query) if query else []
            scored_cards = []

            for row in rows:
                card = dict(row)
                try:
                    card["source_ids"] = json.loads(card["source_ids"])
                except Exception:
                    card["source_ids"] = []

                # Read or generate card embedding
                card_emb = None
                if "embedding" in card and card["embedding"]:
                    try:
                        card_emb = json.loads(card["embedding"])
                    except Exception:
                        pass

                if not card_emb:
                    combined_text = f"{card['title']} {card['summary']} {card['body']}"
                    card_emb = self.embedder.get_embedding(combined_text)
                    self._update_card_embedding_in_db(card["card_id"], json.dumps(card_emb))

                # Sparse keyword scoring
                score = 0.0
                title_lower = card["title"].lower()
                summary_lower = card["summary"].lower()
                body_lower = card["body"].lower()

                for token in query_tokens:
                    if token in title_lower:
                        score += 3.0
                    if token in summary_lower:
                        score += 2.0
                    if token in body_lower:
                        score += 1.0

                if procedure_ids:
                    for pid in procedure_ids:
                        if pid.lower() in card["body"].lower() or pid.lower() in card["summary"].lower():
                            score += 5.0

                # Dense semantic scoring
                semantic_boost = 0.0
                if query_emb and card_emb:
                    similarity = self.embedder.cosine_similarity(query_emb, card_emb)
                    # scale similarity * 15.0 for dynamic semantic boost
                    semantic_boost = similarity * 15.0

                score += semantic_boost

                confidence_multiplier = 0.5 + (card["confidence"] * 0.5)
                final_score = score * confidence_multiplier

                card["_score"] = final_score
                card["_semantic_boost"] = semantic_boost
                scored_cards.append(card)

            scored_cards.sort(key=lambda x: (x["_score"], x["confidence"]), reverse=True)

            results = []
            total_chars = 0

            # Dynamic context budget assembly: slice cards dynamically
            for card in scored_cards:
                if len(results) >= limit:
                    break

                card_size = len(card["title"]) + len(card["summary"]) + len(card["body"])
                # Only include within character budget to prevent prompt paralysis
                if total_chars + card_size <= context_budget_chars:
                    reason = "Matched query keywords."
                    if card["_score"] > 5.0:
                        reason = "Strong relevance based on overlap and procedures."
                    if card.get("_semantic_boost", 0.0) > 1.0:
                        reason += f" (Semantic similarity boost applied: {card['_semantic_boost']:.2f})"

                    results.append({
                        "card_id": card["card_id"],
                        "card_type": card["card_type"],
                        "title": card["title"],
                        "summary": card["summary"],
                        "body": card["body"],
                        "confidence": card["confidence"],
                        "validation_state": card["validation_state"],
                        "source_ids": card["source_ids"],
                        "reason_selected": reason
                    })
                    total_chars += card_size

            return {
                "memory_context": results,
                "retrieved_card_ids": [c["card_id"] for c in results],
                "retrieval_count": len(results),
                "total_chars_utilized": total_chars
            }
        finally:
            conn.close()

    def ingest_worker_report(
        self,
        report: Dict[str, Any],
        source_worker: str,
        review: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Idempotent ingestion of Worker Reports.
        If candidate_learning is true, extracts a candidate DRAFT Knowledge Card.
        """
        report_id = report.get("report_id")
        if not report_id:
            raise ValueError("report_id is required for ingestion.")

        conn = self.db.get_connection()
        try:
            with conn:
                # Check for existing report
                cursor = conn.execute("SELECT report_id FROM worker_reports WHERE report_id = ?", (report_id,))
                if cursor.fetchone():
                    # Idempotent: return existing draft cards generated by this report
                    card_cursor = conn.execute("SELECT * FROM knowledge_cards WHERE source_ids LIKE ?", (f'%"{report_id}"%',))
                    existing_cards = []
                    for r in card_cursor.fetchall():
                        c = dict(r)
                        c["source_ids"] = json.loads(c["source_ids"])
                        existing_cards.append(c)
                    return existing_cards

                # Save report
                conn.execute("""
                    INSERT INTO worker_reports (
                        report_id, task_id, procedure_ids, worker_id, worker_type,
                        started_at, completed_at, outcome, attempted, succeeded,
                        failed, root_cause, repair_action, evidence, changed_files,
                        test_results, security_classification, candidate_learning, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    report_id,
                    report.get("task_id", ""),
                    json.dumps(report.get("procedure_ids", [])),
                    report.get("worker_id", source_worker),
                    report.get("worker_type", "GENERIC"),
                    report.get("started_at", datetime.utcnow().isoformat()),
                    report.get("completed_at", datetime.utcnow().isoformat()),
                    report.get("outcome", "SUCCESS"),
                    report.get("attempted", ""),
                    report.get("succeeded", ""),
                    report.get("failed", ""),
                    report.get("root_cause"),
                    report.get("repair_action"),
                    json.dumps(report.get("evidence", [])),
                    json.dumps(report.get("changed_files", [])),
                    json.dumps(report.get("test_results", {})),
                    report.get("security_classification", "INTERNAL"),
                    1 if report.get("candidate_learning", True) else 0,
                    datetime.utcnow().isoformat()
                ))

                # Generate Candidate Draft Card if learning is enabled
                draft_cards = []
                if report.get("candidate_learning", True):
                    card_id = f"KC-DRAFT-{report_id}"
                    outcome = report.get("outcome", "SUCCESS")

                    # Select Card Family rigidly based on outcome and attributes
                    if outcome == "FAILURE" or report.get("repair_action"):
                        card_type = "REPAIR"
                    else:
                        card_type = "PROCEDURE"

                    title = f"Candidate Learning from {report.get('task_id', 'Task')}"
                    summary = f"Automatically extracted from worker report of {report_id}."

                    body = (
                        f"Attempted: {report.get('attempted', '')}\n"
                        f"Succeeded: {report.get('succeeded', '')}\n"
                        f"Failed: {report.get('failed', '')}\n"
                        f"Root Cause: {report.get('root_cause', 'N/A')}\n"
                        f"Repair Action: {report.get('repair_action', 'N/A')}"
                    )

                    confidence = 0.8 if outcome == "SUCCESS" else 0.5

                    combined_text = f"{title} {summary} {body}"
                    card_emb = self.embedder.get_embedding(combined_text)
                    card_emb_json = json.dumps(card_emb)

                    # Insert draft card
                    conn.execute("""
                        INSERT INTO knowledge_cards (
                            card_id, card_type, title, summary, body, confidence,
                            validation_state, security_classification, source_ids,
                            created_at, updated_at, embedding
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        card_id,
                        card_type,
                        title,
                        summary,
                        body,
                        confidence,
                        "DRAFT",
                        report.get("security_classification", "INTERNAL"),
                        json.dumps([report_id]),
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat(),
                        card_emb_json
                    ))

                    # Insert initial revision
                    conn.execute("""
                        INSERT INTO revisions (
                            card_id, version, title, summary, body, confidence,
                            validation_state, security_classification, modifier, reason, created_at, embedding
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        card_id,
                        1,
                        title,
                        summary,
                        body,
                        confidence,
                        "DRAFT",
                        report.get("security_classification", "INTERNAL"),
                        source_worker,
                        "Initial draft extracted from worker report.",
                        datetime.utcnow().isoformat(),
                        card_emb_json
                    ))

                    draft_cards.append({
                        "card_id": card_id,
                        "card_type": card_type,
                        "title": title,
                        "summary": summary,
                        "body": body,
                        "confidence": confidence,
                        "validation_state": "DRAFT",
                        "security_classification": report.get("security_classification", "INTERNAL"),
                        "source_ids": [report_id]
                    })

                return draft_cards
        finally:
            conn.close()

    def review_card(
        self,
        card_id: str,
        action: str, # e.g. "APPROVE", "ACTIVATE", "REJECT"
        reviewer: str,
        notes: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transition a card through the Review Gate: DRAFT -> REVIEWED -> APPROVED -> ACTIVE.
        Creates immutable revision record.
        """
        action = action.upper()
        conn = self.db.get_connection()
        try:
            with conn:
                cursor = conn.execute("SELECT * FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Card {card_id} not found.")

                card = dict(row)
                current_state = card["validation_state"]

                if action == "REJECT":
                    if not reason:
                        raise ValueError("Reason is required for rejections.")
                    target_state = "REJECTED"
                elif action == "DEPRECATE":
                    target_state = "DEPRECATED"
                elif action == "REVIEW":
                    if current_state != "DRAFT":
                        raise ValueError(f"Cannot transition to REVIEWED from state {current_state}.")
                    target_state = "REVIEWED"
                elif action == "APPROVE":
                    if current_state not in ("DRAFT", "REVIEWED"):
                        raise ValueError(f"Cannot transition to APPROVED from state {current_state}.")
                    target_state = "APPROVED"
                elif action == "ACTIVATE":
                    target_state = "ACTIVE"
                else:
                    raise ValueError(f"Unknown review action {action}.")

                rev_cursor = conn.execute("SELECT MAX(version) as max_v FROM revisions WHERE card_id = ?", (card_id,))
                rev_row = rev_cursor.fetchone()
                next_version = (rev_row["max_v"] or 0) + 1

                # Update card
                conn.execute("""
                    UPDATE knowledge_cards
                    SET validation_state = ?, updated_at = ?
                    WHERE card_id = ?
                """, (target_state, datetime.utcnow().isoformat(), card_id))

                # Insert revision record
                conn.execute("""
                    INSERT INTO revisions (
                        card_id, version, title, summary, body, confidence,
                        validation_state, security_classification, modifier, reason, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    card_id,
                    next_version,
                    card["title"],
                    card["summary"],
                    card["body"],
                    card["confidence"],
                    target_state,
                    card["security_classification"],
                    reviewer,
                    notes or reason or f"Transitioned to {target_state} via {action} action.",
                    datetime.utcnow().isoformat()
                ))

                # Insert review entry
                review_id = f"REV-{card_id}-{next_version}"
                conn.execute("""
                    INSERT INTO reviews (
                        review_id, card_id, reviewer, decision, notes, reason, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    review_id,
                    card_id,
                    reviewer,
                    target_state,
                    notes,
                    reason,
                    datetime.utcnow().isoformat()
                ))

                card["validation_state"] = target_state
                card["source_ids"] = json.loads(card["source_ids"])
                return card
        finally:
            conn.close()

    def get_worker_modes(self) -> List[Dict[str, Any]]:
        """Retrieves all registered worker modes from the database."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM worker_modes")
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch worker modes: {str(e)}")
            return []
        finally:
            conn.close()

    def update_worker_mode(self, worker_id: str, mode: str) -> bool:
        """Dynamically updates the operational mode of a specific worker."""
        conn = self.db.get_connection()
        try:
            with conn:
                cursor = conn.execute("SELECT worker_id FROM worker_modes WHERE worker_id = ?", (worker_id.lower(),))
                if not cursor.fetchone():
                    return False
                conn.execute("""
                    UPDATE worker_modes
                    SET mode = ?, updated_at = ?
                    WHERE worker_id = ?
                """, (mode.upper(), datetime.utcnow().isoformat(), worker_id.lower()))
            return True
        except Exception as e:
            logger.error(f"Failed to update worker mode for {worker_id}: {str(e)}")
            return False
        finally:
            conn.close()

    def health(self) -> Dict[str, Any]:
        """Returns connection status, database statistics, and migration information."""
        try:
            conn = self.db.get_connection()
            try:
                mig_cursor = conn.execute("SELECT MAX(version) as v FROM migrations")
                mig_row = mig_cursor.fetchone()
                schema_v = str(mig_row["v"]) if mig_row and mig_row["v"] is not None else "0"

                cnt_cursor = conn.execute("SELECT COUNT(*) as cnt FROM knowledge_cards")
                cnt_row = cnt_cursor.fetchone()
                card_count = cnt_row["cnt"] if cnt_row else 0

                link_cursor = conn.execute("SELECT COUNT(*) as cnt FROM card_links")
                link_row = link_cursor.fetchone()
                link_count = link_row["cnt"] if link_row else 0

                return {
                    "connected": True,
                    "schema_version": schema_v,
                    "card_count": card_count,
                    "link_count": link_count,
                    "database_path": self.db_path
                }
            finally:
                conn.close()
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
