import os
import re
import datetime
from typing import List, Dict, Any
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

class DoctrineImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def parse_card_id(self, filepath: str, content: str) -> str:
        """Attempts to parse card ID (e.g. PC-AC-01 or PC-SO-01) from markdown text, otherwise derives one from the filename."""
        # Search for pattern '- **Card ID:** PC-XX-XX' or 'Card ID: PC-XX-XX'
        match = re.search(r"(?i)card[-_\s]id:\s*([A-Za-z0-9\-]+)", content)
        if match:
            return match.group(1).strip()

        # Fallback to filename
        base = os.path.basename(filepath)
        name, _ = os.path.splitext(base)
        # clean the name to create a nice uppercase id, prefixing with LEGACY
        clean_name = re.sub(r"[^a-zA-Z0-9\-]", "_", name).upper()
        return f"PC-LEGACY-{clean_name}"

    def classify_file(self, filepath: str) -> str:
        """Classifies a document first before importing it. Do not silently convert everything blindly."""
        normalized_path = filepath.lower()
        if "checklist" in normalized_path:
            return "SKILL"  # checklists represent standard operating skills/procedures
        if "identity" in normalized_path or "soul" in normalized_path:
            return "KNOWLEDGE"  # identity or soul is core knowledge doctrine
        if "agents" in normalized_path:
            return "DECISION"  # agents rules represent governance decisions
        return "KNOWLEDGE"

    def import_file(self, filepath: str) -> KnowledgeCard:
        """
        Parses a single Markdown file safely as read-only, classifies it,
        creates a corresponding KnowledgeCard marked as legacy doctrine,
        and saves it to the database.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Markdown file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        card_id = self.parse_card_id(filepath, content)
        card_type = self.classify_file(filepath)

        # Try to extract the first line as a title
        title = "Legacy Doctrine"
        first_line_match = re.search(r"^#+\s*(.*)", content)
        if first_line_match:
            title = first_line_match.group(1).strip()

        # Generate standard description summary
        summary = f"Legacy doctrine imported from {os.path.basename(filepath)}."
        # Grab the first 200 characters of non-header lines as summary fallback
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            summary = " ".join(lines[:3])[:250] + "..."

        now_str = datetime.datetime.utcnow().isoformat() + "Z"

        card = KnowledgeCard(
            card_id=card_id,
            card_type=card_type,
            schema_version="1.0.0",
            title=f"Doctrine: {title}",
            summary=summary,
            body=content,
            status="APPROVED",  # Existing, trusted doctrine is pre-approved
            confidence=1.0,     # Maximum confidence for canonical doctrine
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
            problem_solved=f"Preserves {os.path.basename(filepath)} operational guidance.",
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
        imported_cards = []
        if not os.path.exists(dir_path):
            return []

        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    try:
                        card = self.import_file(full_path)
                        imported_cards.append(card)
                    except Exception as e:
                        # Log and continue so minor parsing issues in one file don't halt import
                        print(f"Error importing {full_path}: {e}")

        return imported_cards
