import json
from typing import List, Dict, Any, Optional
from solomon_knowledge_cards.models import KnowledgeCardModel, CardStatus
from solomon_knowledge_cards.db import SQLiteDatabase

class KnowledgeRepository:
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def create_card(self, card: KnowledgeCardModel, actor: str = "SYSTEM") -> None:
        """Create a new card with DRAFT status."""
        card.status = CardStatus.DRAFT
        self.db.save_card(card, actor=actor)

    def get_card(self, card_id: str) -> Optional[KnowledgeCardModel]:
        return self.db.get_card(card_id)

    def update_card(self, card: KnowledgeCardModel, actor: str = "SYSTEM") -> None:
        self.db.save_card(card, actor=actor)

    def deprecate_card(self, card_id: str, actor: str = "SYSTEM") -> None:
        """Deprecate card safely."""
        card = self.get_card(card_id)
        if card:
            card.status = CardStatus.DEPRECATED
            self.db.save_card(card, actor=actor)

    def list_cards(self, include_deprecated: bool = True) -> List[KnowledgeCardModel]:
        cards = self.db.list_all_cards()
        if not include_deprecated:
            cards = [c for cards in cards if c.status != CardStatus.DEPRECATED]
        return cards

    def search_by_text(self, query: str) -> List[KnowledgeCardModel]:
        """Performs precise case-insensitive keyword searching across card titles, summaries, and bodies."""
        all_cards = self.list_cards()
        matches = []
        query_lower = query.lower()
        for card in all_cards:
            if (query_lower in card.title.lower() or
                query_lower in card.summary.lower() or
                query_lower in card.body.lower()):
                matches.append(card)
        return matches

    def search_by_type(self, card_type: str) -> List[KnowledgeCardModel]:
        all_cards = self.list_cards()
        return [c for c in all_cards if c.card_type == card_type]

    def search_by_tags(self, tags: List[str]) -> List[KnowledgeCardModel]:
        all_cards = self.list_cards()
        matches = []
        tags_set = set(t.lower() for t in tags)
        for card in all_cards:
            card_tags_set = set(t.lower() for t in card.tags)
            if tags_set.intersection(card_tags_set):
                matches.append(card)
        return matches

    def search_by_source(self, source_id: str) -> List[KnowledgeCardModel]:
        all_cards = self.list_cards()
        matches = []
        for card in all_cards:
            if source_id in card.source_ids:
                matches.append(card)
        return matches

    def link_cards(self, parent_id: str, child_id: str, relation_type: str, actor: str = "SYSTEM") -> None:
        """Dynamically link cards together to track linear dependencies and parent relationships."""
        parent = self.get_card(parent_id)
        child = self.get_card(child_id)
        if not parent or not child:
            raise ValueError("Both parent and child cards must exist in order to link them.")

        # Update lists to establish directed link edges
        if child_id not in parent.related_card_ids:
            parent.related_card_ids.append(child_id)
        if parent_id not in child.parent_card_ids:
            child.parent_card_ids.append(parent_id)

        # Store linking reason/type in metadata
        if "links" not in parent.metadata:
            parent.metadata["links"] = {}
        parent.metadata["links"][child_id] = relation_type

        self.update_card(parent, actor=actor)
        self.update_card(child, actor=actor)

    def retrieve_related_cards(self, card_id: str) -> List[KnowledgeCardModel]:
        """Fetch all directly connected or nested related cards (1-hop traversal)."""
        card = self.get_card(card_id)
        if not card:
            return []
        related_ids = set(card.parent_card_ids + card.related_card_ids)
        related_cards = []
        for r_id in related_ids:
            r_card = self.get_card(r_id)
            if r_card:
                related_cards.append(r_card)
        return related_cards

    def get_revision_history(self, card_id: str) -> List[Dict[str, Any]]:
        return self.db.get_revision_history(card_id)

    def export_cards(self, filepath: str) -> None:
        self.db.export_to_jsonl(filepath)

    def import_cards(self, filepath: str) -> None:
        self.db.import_from_jsonl(filepath)
