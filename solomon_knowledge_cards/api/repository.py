import re
from typing import List, Dict, Any, Optional
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard
from solomon_knowledge_cards.api.embeddings import SemanticEmbedder

class CardRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.embedder = SemanticEmbedder()
        self.db_manager = db_manager

    def create_card(self, card: KnowledgeCard, creator: str = "system", reason: Optional[str] = None) -> None:
        """Creates a new card in the storage layer."""
        if not card.embedding:
            combined_text = f"{card.title} {card.summary} {card.why_created} {card.problem_solved} {card.body}"
            card.embedding = self.embedder.generate_embedding(combined_text)
        self.db_manager.store_card(card, updater=creator, reason=reason or "Initial creation")

    def get_card(self, card_id: str) -> Optional[KnowledgeCard]:
        """Reads a card by ID."""
        return self.db_manager.get_card(card_id)

    def update_card(self, card: KnowledgeCard, updater: str = "system", reason: Optional[str] = None) -> None:
        """Updates an existing card in the database, appending to revision history."""
        existing = self.db_manager.get_card(card.card_id)
        if not existing:
            raise ValueError(f"Card {card.card_id} does not exist. Use create_card first.")

        # Re-generate embedding on update
        combined_text = f"{card.title} {card.summary} {card.why_created} {card.problem_solved} {card.body}"
        card.embedding = self.embedder.generate_embedding(combined_text)

        self.db_manager.store_card(card, updater=updater, reason=reason or "Card update")

    def deprecate_card(self, card_id: str, updater: str = "system", reason: Optional[str] = None) -> bool:
        """Deprecates/soft-deletes a card."""
        return self.db_manager.soft_delete_card(card_id, updater=updater, reason=reason)

    def list_cards(self, include_deleted: bool = False) -> List[KnowledgeCard]:
        """Lists all stored cards."""
        return self.db_manager.list_all_cards(include_deleted=include_deleted)

    def link_cards(self, source_id: str, target_id: str, link_type: str, updater: str = "system", reason: Optional[str] = None) -> None:
        """Links two cards together (e.g. source_id links to target_id with link_type)."""
        source_card = self.db_manager.get_card(source_id)
        target_card = self.db_manager.get_card(target_id)
        if not source_card:
            raise ValueError(f"Source card {source_id} does not exist.")
        if not target_card:
            raise ValueError(f"Target card {target_id} does not exist.")

        if link_type == "PARENT":
            if target_id not in source_card.parent_card_ids:
                source_card.parent_card_ids.append(target_id)
        elif link_type == "RELATED":
            if target_id not in source_card.related_card_ids:
                source_card.related_card_ids.append(target_id)
        elif link_type in ("DEPENDS_ON", "PREVENTS", "ENHANCES"):
            with self.db_manager._lock:
                conn = self.db_manager._get_connection()
                try:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, ?)", (source_id, target_id, link_type))
                    conn.commit()
                finally:
                    conn.close()
            return # Don't need to re-save the source card fully
        else:
            raise ValueError(f"Unsupported link type: {link_type}")

        self.db_manager.store_card(source_card, updater=updater, reason=reason or f"Linked to {target_id}")

    def get_related_cards(self, card_id: str) -> List[KnowledgeCard]:
        """Retrieves linked parent and related cards of a given card."""
        card = self.get_card(card_id)
        if not card:
            return []
        related = []
        for p_id in card.parent_card_ids:
            p_card = self.get_card(p_id)
            if p_card:
                related.append(p_card)
        for r_id in card.related_card_ids:
            r_card = self.get_card(r_id)
            if r_card:
                related.append(r_card)

        # Also grab any semantic relationships from the DB directly
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT target_id FROM card_links WHERE source_id = ? AND link_type IN ('DEPENDS_ON', 'PREVENTS', 'ENHANCES')", (card_id,))
                for row in cursor.fetchall():
                    target_id = row[0]
                    t_card = self.get_card(target_id)
                    if t_card and target_id not in [c.card_id for c in related]:
                        related.append(t_card)
            finally:
                conn.close()

        return related

    def retrieve_revision_history(self, card_id: str) -> List[Dict[str, Any]]:
        """Retrieves full revision log of a card."""
        return self.db_manager.get_revision_history(card_id)

    def export_cards(self, filepath: str) -> None:
        """Exports repository to JSONL."""
        self.db_manager.export_to_jsonl(filepath)

    def import_cards(self, filepath: str, updater: str = "importer") -> None:
        """Imports cards from JSONL."""
        self.db_manager.import_from_jsonl(filepath, updater=updater)

    def search_by_type(self, card_type: str) -> List[KnowledgeCard]:
        """Returns all cards of a given type."""
        return [c for c in self.list_cards() if c.card_type.upper() == card_type.upper()]

    def search_by_tags(self, tags: List[str]) -> List[KnowledgeCard]:
        """Returns all cards matching any of the specified tags."""
        normalized_tags = [t.lower() for t in tags]
        results = []
        for c in self.list_cards():
            if any(ct.lower() in normalized_tags for ct in c.tags):
                results.append(c)
        return results

    def search_by_source(self, source_id: str) -> List[KnowledgeCard]:
        """Returns all cards associated with a given source ID (e.g. worker report or task id)."""
        results = []
        for c in self.list_cards():
            if source_id in c.source_ids:
                results.append(c)
        return results

    def search(
        self,
        query: str,
        card_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_classification: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs keyword-based search with field weighting, ranking, and explanation.
        Query terms are matched against title, summary, body, tags, and 'why_created', 'problem_solved'.
        """
        all_cards = self.list_cards()
        ranked_results = []


        # Tokenize query
        terms = [t.lower() for t in re.findall(r'\w+', query)] if query else []

        # Generate query embedding if terms exist
        query_embedding = self.embedder.generate_embedding(query) if query else None

        for card in all_cards:
            # Type filter
            if card_type and card.card_type.upper() != card_type.upper():
                continue

            # Tags filter (must match at least one if tags filter is provided)
            if tags and not any(t.lower() in [ct.lower() for ct in card.tags] for t in tags):
                continue

            # Security classification filter
            if security_classification and card.security_classification != security_classification:
                continue

            score = 0.0
            explanations = []


            # Keyword matching and scoring
            semantic_score = 0.0
            if query_embedding and card.embedding:
                semantic_similarity = self.embedder.compute_similarity(query_embedding, card.embedding)
                if semantic_similarity > 0.5:  # Threshold
                    semantic_score = semantic_similarity * 20.0
                    explanations.append(f"Semantic similarity match (+{semantic_score:.1f} pts)")
                    score += semantic_score

            if terms:
                title_matches = 0
                summary_matches = 0
                body_matches = 0
                tag_matches = 0
                rationale_matches = 0

                # Title (weight: 10)
                for term in terms:
                    count = card.title.lower().count(term)
                    if count > 0:
                        title_matches += count
                        score += count * 10.0
                if title_matches:
                    explanations.append(f"Matched terms in Title ({title_matches} times, +{title_matches * 10:.1f} pts)")

                # Summary (weight: 5)
                for term in terms:
                    count = card.summary.lower().count(term)
                    if count > 0:
                        summary_matches += count
                        score += count * 5.0
                if summary_matches:
                    explanations.append(f"Matched terms in Summary ({summary_matches} times, +{summary_matches * 5:.1f} pts)")

                # Body (weight: 2)
                for term in terms:
                    count = card.body.lower().count(term)
                    if count > 0:
                        body_matches += count
                        score += count * 2.0
                if body_matches:
                    explanations.append(f"Matched terms in Body ({body_matches} times, +{body_matches * 2:.1f} pts)")

                # Tags (weight: 8)
                for term in terms:
                    for tag in card.tags:
                        if term in tag.lower():
                            tag_matches += 1
                            score += 8.0
                if tag_matches:
                    explanations.append(f"Matched terms in Tags ({tag_matches} times, +{tag_matches * 8:.1f} pts)")

                # Rationale / "Why does this exist" fields (weight: 6)
                for term in terms:
                    for field_val in [card.why_created, card.problem_solved, card.future_work_dependent]:
                        count = field_val.lower().count(term)
                        if count > 0:
                            rationale_matches += count
                            score += count * 6.0
                if rationale_matches:
                    explanations.append(f"Matched terms in Rationale fields ({rationale_matches} times, +{rationale_matches * 6:.1f} pts)")
            else:
                # If no query string, base score is confidence * 10
                score = card.confidence * 10.0
                explanations.append(f"Default ranking based on confidence score (Score: {score:.1f})")

            # Multiply or adjust score by card confidence to factor correctness
            confidence_multiplier = 0.5 + (card.confidence * 0.5)  # maps [0,1] to [0.5, 1]
            final_score = score * confidence_multiplier

            if terms and final_score == 0.0:
                # Filter out completely irrelevant results when keyword search is active
                continue

            explanation_str = "; ".join(explanations) if explanations else "No matched terms."

            ranked_results.append({
                "card": card.to_dict(),
                "card_id": card.card_id,
                "card_type": card.card_type,
                "confidence": card.confidence,
                "validation_state": card.validation_state,
                "score": final_score,
                "explanation": f"{explanation_str} [Confidence Multiplier: {confidence_multiplier:.2f}]"
            })

        # Rank by score descending, then by confidence descending
        ranked_results.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
        return ranked_results
