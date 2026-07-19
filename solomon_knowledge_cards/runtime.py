import os
import json
import sqlite3
import hmac
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import DatabaseManager

CLEARANCE_ORDER = ["PUBLIC", "INTERNAL", "RESTRICTED"]

def get_allowed_clearances(clearance: str) -> List[str]:
    c = (clearance or "INTERNAL").upper()
    if c not in CLEARANCE_ORDER:
        c = "INTERNAL"
    idx = CLEARANCE_ORDER.index(c)
    return CLEARANCE_ORDER[:idx + 1]

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

    def retrieve_context(
        self,
        query: str,
        clearance: str,
        task_type: Optional[str] = None,
        procedure_ids: Optional[List[str]] = None,
        limit: int = 3,
    ) -> Dict[str, Any]:
        """
        Retrieves approved/active valid knowledge cards matching search query and clearance level.
        Only retrieves APPROVED or ACTIVE cards.
        """
        allowed = get_allowed_clearances(clearance)
        placeholders = ",".join("?" for _ in allowed)

        conn = self.db.get_connection()
        try:
            # Query all eligible cards
            # We filter by validation_state IN ('APPROVED', 'ACTIVE') and clearance
            sql = f"""
                SELECT * FROM knowledge_cards
                WHERE validation_state IN ('APPROVED', 'ACTIVE')
                  AND security_classification IN ({placeholders})
            """
            params = list(allowed)

            if task_type:
                sql += " AND card_type = ?"
                params.append(task_type)

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            # Rank rows based on a basic token matching score
            query_tokens = [t.lower() for t in query.split() if t]
            scored_cards = []

            for row in rows:
                card = dict(row)
                # Decode source_ids
                try:
                    card["source_ids"] = json.loads(card["source_ids"])
                except Exception:
                    card["source_ids"] = []

                # Calculate match score
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

                # Check procedure_ids overlapping if supplied
                if procedure_ids:
                    # Procedure_ids overlapping score bonus
                    for pid in procedure_ids:
                        if pid.lower() in card["body"].lower() or pid.lower() in card["summary"].lower():
                            score += 5.0

                card["_score"] = score
                scored_cards.append(card)

            # Sort by score descending, then by confidence descending, then by card_id
            scored_cards.sort(key=lambda x: (x["_score"], x["confidence"]), reverse=True)

            # Slice to limit
            results = scored_cards[:limit]

            # Construct safe explanations and return bundles
            retrieved_cards = []
            for card in results:
                # Build safe selected reason
                reason = "Matched query keywords."
                if card["_score"] > 5.0:
                    reason = "Strong relevance based on overlap and procedures."

                retrieved_cards.append({
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

            return {
                "memory_context": retrieved_cards,
                "retrieved_card_ids": [c["card_id"] for c in retrieved_cards],
                "retrieval_count": len(retrieved_cards)
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
                    # Formulate draft card contents based on report outcome
                    card_id = f"KC-DRAFT-{report_id}"
                    outcome = report.get("outcome", "SUCCESS")
                    card_type = "REPAIR" if outcome == "FAILURE" or report.get("repair_action") else "PROCEDURE"

                    title = f"Candidate Learning from {report.get('task_id', 'Task')}"
                    summary = f"Automatically extracted from worker report of {report_id}."

                    # Ensure secret redaction in body/summary
                    body = (
                        f"Attempted: {report.get('attempted', '')}\n"
                        f"Succeeded: {report.get('succeeded', '')}\n"
                        f"Failed: {report.get('failed', '')}\n"
                        f"Root Cause: {report.get('root_cause', 'N/A')}\n"
                        f"Repair Action: {report.get('repair_action', 'N/A')}"
                    )

                    confidence = 0.8 if outcome == "SUCCESS" else 0.5

                    # Insert draft card
                    conn.execute("""
                        INSERT INTO knowledge_cards (
                            card_id, card_type, title, summary, body, confidence,
                            validation_state, security_classification, source_ids,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                        datetime.utcnow().isoformat()
                    ))

                    # Insert initial revision
                    conn.execute("""
                        INSERT INTO revisions (
                            card_id, version, title, summary, body, confidence,
                            validation_state, security_classification, modifier, reason, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                        datetime.utcnow().isoformat()
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
                # Find card
                cursor = conn.execute("SELECT * FROM knowledge_cards WHERE card_id = ?", (card_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Card {card_id} not found.")

                card = dict(row)
                current_state = card["validation_state"]

                # Determine target validation state
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
                    # For activation, can come from DRAFT, REVIEWED, or APPROVED
                    target_state = "ACTIVE"
                else:
                    raise ValueError(f"Unknown review action {action}.")

                # Generate next revision version
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

    def health(self) -> Dict[str, Any]:
        """Returns connection status, database statistics, and migration information."""
        try:
            conn = self.db.get_connection()
            try:
                # Query migration version
                mig_cursor = conn.execute("SELECT MAX(version) as v FROM migrations")
                mig_row = mig_cursor.fetchone()
                schema_v = str(mig_row["v"]) if mig_row and mig_row["v"] is not None else "0"

                # Query card count
                cnt_cursor = conn.execute("SELECT COUNT(*) as cnt FROM knowledge_cards")
                cnt_row = cnt_cursor.fetchone()
                card_count = cnt_row["cnt"] if cnt_row else 0

                return {
                    "connected": True,
                    "schema_version": schema_v,
                    "card_count": card_count,
                    "database_path": self.db_path
                }
            finally:
                conn.close()
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
