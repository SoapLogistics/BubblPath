import os
import re
import datetime
from typing import List, Dict, Any
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard

def validate_safe_path(filepath: str, allowed_base_dir: str = ".") -> str:
    """
    Validates that a file path is safe from path traversal attacks.
    Ensures the path resides strictly within the allowed base directory boundary
    and contains no traversal elements like '..' or absolute root routes.
    """
    abs_base = os.path.abspath(allowed_base_dir)
    abs_file = os.path.abspath(filepath)

    # Check for direct path traversal tricks
    if ".." in filepath or filepath.startswith(("/", "\\")):
        # If absolute, it must start with the base directory path
        if not abs_file.startswith(abs_base):
            raise ValueError(f"Security Violation: Path traversal attempt blocked: {filepath}")

    if not abs_file.startswith(abs_base):
        raise ValueError(f"Security Violation: Path falls outside allowed base directory: {filepath}")

    return abs_file

class DoctrineImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def parse_card_id(self, filepath: str, content: str) -> str:
        """Attempts to parse card ID from markdown text safely."""
        match = re.search(r"(?i)card[-_\s]id:\s*([A-Za-z0-9\-]+)", content)
        if match:
            # Prevent injection of weird strings into card ID
            clean_id = re.sub(r"[^a-zA-Z0-9\-]", "", match.group(1).strip())
            return clean_id

        base = os.path.basename(filepath)
        name, _ = os.path.splitext(base)
        clean_name = re.sub(r"[^a-zA-Z0-9\-]", "_", name).upper()
        return f"PC-LEGACY-{clean_name}"

    def classify_file(self, filepath: str) -> str:
        """Classifies a document first before importing it."""
        normalized_path = filepath.lower()
        if "checklist" in normalized_path:
            return "SKILL"
        if "identity" in normalized_path or "soul" in normalized_path:
            return "KNOWLEDGE"
        if "agents" in normalized_path:
            return "DECISION"
        return "KNOWLEDGE"

    def import_file(self, filepath: str) -> KnowledgeCard:
        """
        Parses a single Markdown file safely as read-only with path traversal checks,
        classifies it, and saves it.
        """
        # Strictly validate filepath against path traversal before any OS read actions
        safe_path = validate_safe_path(filepath)

        if not os.path.exists(safe_path):
            raise FileNotFoundError(f"Markdown file not found: {filepath}")

        with open(safe_path, "r", encoding="utf-8") as f:
            content = f.read()

        card_id = self.parse_card_id(safe_path, content)
        card_type = self.classify_file(safe_path)

        # Safe regex Title extraction
        title = "Legacy Doctrine"
        first_line_match = re.search(r"^#+\s*(.*)", content)
        if first_line_match:
            title = re.sub(r"[<>`\"'%;()&]", "", first_line_match.group(1).strip()) # sanitize basic HTML/shell chars

        summary = f"Legacy doctrine imported from {os.path.basename(safe_path)}."
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            summary = re.sub(r"[<>`\"'%;()&]", "", " ".join(lines[:3])[:250]) + "..."

        now_str = datetime.datetime.now(datetime.UTC).isoformat()

        card = KnowledgeCard(
            card_id=card_id,
            card_type=card_type,
            schema_version="1.0.0",
            title=f"Doctrine: {title}",
            summary=summary,
            body=content,
            status="APPROVED",
            confidence=1.0,
            validation_state="VALID",
            created_at=now_str,
            updated_at=now_str,
            created_by="doctrine_importer",
            source_type="LEGACY_DOCTRINE",
            source_ids=[filepath],
            parent_card_ids=[],
            related_card_ids=[],
            tags=["legacy", "doctrine", "imported", card_type.lower()],
            security_classification="INTERNAL",
            evidence=f"Verification of existing file system artifact: {filepath}",
            why_created="Imported to establish baseline legacy doctrine in the Knowledge Card DB.",
            problem_solved=f"Preserves {os.path.basename(safe_path)} operational guidance.",
            future_work_dependent="Forms the bedrock of Solomon's retrieval-augmented procedural context.",
            extra_metadata={
                "original_file_path": filepath,
                "imported_at": now_str
            }
        )

        self.db_manager.store_card(card, updater="doctrine_importer", reason="Initial legacy asset migration")
        return card

    def import_directory(self, dir_path: str) -> List[KnowledgeCard]:
        """Recursively finds all .md files in the directory and imports them safely."""
        safe_dir = validate_safe_path(dir_path)
        imported_cards = []
        if not os.path.exists(safe_dir):
            return []

        for root, _, files in os.walk(safe_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    try:
                        card = self.import_file(full_path)
                        imported_cards.append(card)
                    except Exception as e:
                        print(f"Error importing {full_path}: {e}")

        return imported_cards
