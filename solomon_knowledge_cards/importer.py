import os
import re
from typing import List, Dict, Any
from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, ValidationState
from solomon_knowledge_cards.repository import KnowledgeRepository

class DoctrineImporter:
    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def import_checklist_markdown(self, filepath: str) -> KnowledgeCardModel:
        """Parses operational Markdown checklist files, extracting identifiers (PC-SO-XX) and steps without altering files."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Markdown file not found at: {filepath}")

        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse ID from content if present, or assign dynamic legacy name
        pc_match = re.search(r"PC-SO-\d+", content)
        card_id = pc_match.group(0) if pc_match else f"LEGACY-{filename.replace('.md', '').upper()}"

        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"Legacy Operating Doctrine: {filename}"

        summary = f"Legacy protocol checklist imported from {filename}."

        # Instantiate imported legacy procedure card directly as APPROVED (Trusted existing doctrine)
        card = KnowledgeCardModel(
            card_id=card_id,
            card_type=CardType.PROCEDURE,
            title=title,
            summary=summary,
            body=content,
            status=CardStatus.APPROVED,
            confidence=0.9,
            validation_state=ValidationState.HUMAN_VALIDATED,
            created_by="DOCTRINE_IMPORTER",
            source_type="LEGACY_WORKSPACE",
            source_ids=[filepath],
            metadata={"filepath": filepath, "original_filename": filename},
            why_created="To index preexisting workspace checklists as trusted system doctrine.",
            problem_solved="Unified search and cross-referencing for historic playbooks.",
            future_work_dependent="None"
        )

        self.repository.update_card(card, actor="DOCTRINE_IMPORTER")
        return card

    def batch_import_directory(self, directory_path: str) -> List[KnowledgeCardModel]:
        imported_cards = []
        if not os.path.exists(directory_path):
            return imported_cards

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    try:
                        card = self.import_checklist_markdown(full_path)
                        imported_cards.append(card)
                    except Exception:
                        pass
        return imported_cards
