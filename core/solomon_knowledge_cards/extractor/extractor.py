import datetime
import re
import uuid
from typing import Any

from core.solomon_knowledge_cards.models.card import KnowledgeCard


class KnowledgeExtractor:
    def __init__(self, schema_version: str = "1.0.0"):
        self.schema_version = schema_version

    def _parse_markdown_section(self, text: str, header: str) -> str:
        """Helper to extract sections from Markdown text using regex headers."""
        pattern = rf"(?i)(?:^|\n)#+\s*{re.escape(header)}[^\n]*\n(.*?)(?=\n#+|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _is_empty_or_placeholder(self, val: str) -> bool:
        """Determines if a parsed string is empty or just a placeholder like None or N/A."""
        if not val:
            return True
        clean = val.strip().lower()
        return clean in ("", "none", "n/a", "na", "null", "no", "false", "nil")

    def extract_draft_cards(
        self,
        worker_report: Any,
        review_result: Any | None = None,
        creator: str = "extractor"
    ) -> list[KnowledgeCard]:
        """
        Accepts a Worker Report and optional Review Result, parses them, and
        generates draft Knowledge, Failure, Repair, or Lesson Cards in DRAFT status.
        Supports both dictionaries and structured Markdown strings.
        """
        report_data = {}
        review_data = {}

        # 1. Standardize Worker Report input
        if isinstance(worker_report, dict):
            report_data = worker_report
        elif isinstance(worker_report, str):
            # Parse markdown sections
            report_data = {
                "task_id": self._parse_markdown_section(worker_report, "Task ID") or str(uuid.uuid4()),
                "procedure_id": self._parse_markdown_section(worker_report, "Procedure ID") or "PC-GENERIC",
                "outcome": self._parse_markdown_section(worker_report, "Outcome") or "unknown",
                "attempted": self._parse_markdown_section(worker_report, "Attempted"),
                "what_happened": self._parse_markdown_section(worker_report, "What Happened"),
                "succeeded": self._parse_markdown_section(worker_report, "Succeeded"),
                "failed": self._parse_markdown_section(worker_report, "Failed"),
                "root_cause": self._parse_markdown_section(worker_report, "Root Cause"),
                "repair_action": self._parse_markdown_section(worker_report, "Repair Action") or self._parse_markdown_section(worker_report, "Remediation"),
                "evidence": self._parse_markdown_section(worker_report, "Evidence") or "Extracted from worker logs",
                "tags": [t.strip() for t in self._parse_markdown_section(worker_report, "Tags").split(",") if t.strip()]
            }
        else:
            raise TypeError("worker_report must be a dictionary or a string")

        # 2. Standardize Review Result input
        if review_result:
            if isinstance(review_result, dict):
                review_data = review_result
            elif isinstance(review_result, str):
                review_data = {
                    "is_valid": "valid" in self._parse_markdown_section(review_result, "Validation").lower() or "true" in self._parse_markdown_section(review_result, "Validation").lower(),
                    "confidence_score": float(self._parse_markdown_section(review_result, "Confidence") or 0.8),
                    "rejection_reason": self._parse_markdown_section(review_result, "Rejection Reason"),
                    "notes": self._parse_markdown_section(review_result, "Notes")
                }
            else:
                raise TypeError("review_result must be a dictionary or a string")

        # 3. Formulate Card Generation
        generated_cards = []
        now_str = datetime.datetime.now(datetime.UTC).isoformat()

        task_id = report_data.get("task_id", "UNKNOWN_TASK")
        procedure_id = report_data.get("procedure_id", "UNKNOWN_PROCEDURE")
        outcome = str(report_data.get("outcome", "")).lower()

        # Determine classification and type of cards to draft
        confidence = float(review_data.get("confidence_score", 0.7))
        val_state = "UNVALIDATED"
        if review_data:
            val_state = "VALID" if review_data.get("is_valid", False) else "INVALID"

        attempted = report_data.get("attempted", "")
        what_happened = report_data.get("what_happened", "")
        root_cause = report_data.get("root_cause", "")
        repair_action = report_data.get("repair_action", "")
        succeeded_details = report_data.get("succeeded", "")
        failed_details = report_data.get("failed", "")
        evidence = report_data.get("evidence", "No evidence supplied")

        tags = report_data.get("tags", [])
        if not tags:
            tags = ["extracted", outcome]
        else:
            if "extracted" not in tags:
                tags.append("extracted")

        # A. If there is a failure, generate a Failure Card
        has_failed = (outcome == "failure") or (not self._is_empty_or_placeholder(failed_details)) or (not self._is_empty_or_placeholder(root_cause))
        if has_failed:
            fail_id = f"FC-{uuid.uuid4().hex[:8].upper()}"
            fail_card = KnowledgeCard(
                card_id=fail_id,
                card_type="FAILURE",
                schema_version=self.schema_version,
                title=f"Failure during task {task_id}: {report_data.get('title', 'Execution Error')}",
                summary=f"Task {task_id} failed. Succeeded: {succeeded_details}. Failed: {failed_details}.",
                body=f"Attempted: {attempted}\nWhat Happened: {what_happened}\nFailed components: {failed_details}\nRoot Cause: {root_cause}",
                status="DRAFT",
                confidence=confidence,
                validation_state=val_state,
                created_at=now_str,
                updated_at=now_str,
                created_by=creator,
                source_type="WORKER_REPORT",
                source_ids=[task_id, procedure_id],
                parent_card_ids=[],
                related_card_ids=[],
                tags=tags + ["failure"],
                security_classification="INTERNAL",
                evidence=evidence,
                why_created=f"To document the specific failure mode in task {task_id} associated with {procedure_id}.",
                problem_solved=f"Exposes the failure of: {failed_details} due to: {root_cause}.",
                future_work_dependent="Used to avoid this failure pathway in similar future tasks.",
                extra_metadata={
                    "original_report": report_data,
                    "review_result": review_data
                }
            )
            generated_cards.append(fail_card)

            # B. If a repair action exists, generate a corresponding Repair Card
            if not self._is_empty_or_placeholder(repair_action):
                rep_id = f"RC-{uuid.uuid4().hex[:8].upper()}"
                rep_card = KnowledgeCard(
                    card_id=rep_id,
                    card_type="REPAIR",
                    schema_version=self.schema_version,
                    title=f"Remediation playbook for {report_data.get('title', 'Execution Error')}",
                    summary=f"Repair action for failure {fail_id}: {repair_action[:100]}...",
                    body=f"Failure Reference: {fail_id}\nRoot Cause: {root_cause}\nRemediation Actions:\n{repair_action}",
                    status="DRAFT",
                    confidence=confidence,
                    validation_state=val_state,
                    created_at=now_str,
                    updated_at=now_str,
                    created_by=creator,
                    source_type="WORKER_REPORT",
                    source_ids=[task_id, procedure_id],
                    parent_card_ids=[],
                    related_card_ids=[fail_id],
                    tags=tags + ["repair", "remediation"],
                    security_classification="INTERNAL",
                    evidence=f"Validated in task {task_id}. Evidence details: {evidence}",
                    why_created=f"To establish a repeatable hotfix/remediation for failure {fail_id}.",
                    problem_solved=f"Resolves {root_cause} by applying: {repair_action}.",
                    future_work_dependent="Enables self-healing or automatic plan modification when a similar error occurs.",
                    extra_metadata={
                        "original_report": report_data,
                        "review_result": review_data
                    }
                )
                generated_cards.append(rep_card)

        # C. If outcome was successful or we want to capture lessons (and we didn't just fail)
        # Note: If a task partially succeeded but failed, we generated FAILURE/REPAIR. If it fully succeeded, we generate a LESSON.
        is_success = (outcome == "success") or (not self._is_empty_or_placeholder(succeeded_details) and not has_failed)
        if is_success:
            less_id = f"LC-{uuid.uuid4().hex[:8].upper()}"
            less_card = KnowledgeCard(
                card_id=less_id,
                card_type="LESSON",
                schema_version=self.schema_version,
                title=f"Lesson learned from task {task_id}: {report_data.get('title', 'Successful Execution')}",
                summary=f"Task {task_id} completed successfully. Highlight: {succeeded_details[:100]}.",
                body=f"Attempted: {attempted}\nWhat Succeeded: {succeeded_details}\nWhat Happened: {what_happened}",
                status="DRAFT",
                confidence=confidence,
                validation_state=val_state,
                created_at=now_str,
                updated_at=now_str,
                created_by=creator,
                source_type="WORKER_REPORT",
                source_ids=[task_id, procedure_id],
                parent_card_ids=[],
                related_card_ids=[],
                tags=tags + ["lesson", "success"],
                security_classification="INTERNAL",
                evidence=evidence,
                why_created=f"To capture the positive operational lesson and optimizations discovered during task {task_id}.",
                problem_solved=f"Documents what succeeded: {succeeded_details}.",
                future_work_dependent="Can be loaded in planning stages of future tasks to promote successful execution patterns.",
                extra_metadata={
                    "original_report": report_data,
                    "review_result": review_data
                }
            )
            generated_cards.append(less_card)

        # D. Generic knowledge card if neither matches but we have general text
        if not generated_cards:
            k_id = f"KC-{uuid.uuid4().hex[:8].upper()}"
            k_card = KnowledgeCard(
                card_id=k_id,
                card_type="KNOWLEDGE",
                schema_version=self.schema_version,
                title=f"Extracted knowledge from task {task_id}",
                summary=f"Observation in task {task_id}.",
                body=f"Attempted: {attempted}\nWhat Happened: {what_happened}",
                status="DRAFT",
                confidence=0.5,
                validation_state="UNVALIDATED",
                created_at=now_str,
                updated_at=now_str,
                created_by=creator,
                source_type="WORKER_REPORT",
                source_ids=[task_id, procedure_id],
                parent_card_ids=[],
                related_card_ids=[],
                tags=tags,
                security_classification="INTERNAL",
                evidence=evidence,
                why_created="To record observations that do not classify as specific failures or repairs.",
                problem_solved="Captures general execution traces.",
                future_work_dependent="Provides a basis for subsequent reflection or analysis.",
                extra_metadata={
                    "original_report": report_data
                }
            )
            generated_cards.append(k_card)

        return generated_cards
