import re
from typing import List, Dict, Any, Optional
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from core.solomon_knowledge_cards.models.card import KnowledgeCard
from core.solomon_knowledge_cards.api.embeddings import SemanticEmbedder

class CardRepository:
    def __init__(self, db_manager: DatabaseManager, embedder: Optional[SemanticEmbedder] = None):
        self.db_manager = db_manager
        self.embedder = embedder or SemanticEmbedder()

    def create_card(self, card: KnowledgeCard, creator: str = "system", reason: Optional[str] = None) -> None:
        """Creates a new card, automatically generating and attaching its embedding vector."""
        if "embedding" not in card.extra_metadata or not card.extra_metadata["embedding"]:
            combined_text = f"{card.title} {card.summary} {card.body}"
            card.extra_metadata["embedding"] = self.embedder.get_embedding(combined_text)

        self.db_manager.store_card(card, updater=creator, reason=reason or "Initial creation")

    def get_card(self, card_id: str) -> Optional[KnowledgeCard]:
        """Reads a card by ID."""
        return self.db_manager.get_card(card_id)

    def update_card(self, card: KnowledgeCard, updater: str = "system", reason: Optional[str] = None) -> None:
        """Updates a card, regenerating its embedding vector."""
        combined_text = f"{card.title} {card.summary} {card.body}"
        card.extra_metadata["embedding"] = self.embedder.get_embedding(combined_text)

        existing = self.db_manager.get_card(card.card_id)
        if not existing:
            raise ValueError(f"Card {card.card_id} does not exist. Use create_card first.")
        self.db_manager.store_card(card, updater=updater, reason=reason or "Card update")

    def deprecate_card(self, card_id: str, updater: str = "system", reason: Optional[str] = None) -> bool:
        """Deprecates/soft-deletes a card."""
        return self.db_manager.soft_delete_card(card_id, updater=updater, reason=reason)

    def list_cards(self, include_deleted: bool = False) -> List[KnowledgeCard]:
        """Lists all stored cards."""
        return self.db_manager.list_all_cards(include_deleted=include_deleted)

    def link_cards(self, source_id: str, target_id: str, link_type: str, updater: str = "system", reason: Optional[str] = None) -> None:
        """Links two cards together."""
        source_card = self.db_manager.get_card(source_id)
        target_card = self.db_manager.get_card(target_id)
        if not source_card:
            raise ValueError(f"Source card {source_id} does not exist.")
        if not target_card:
            raise ValueError(f"Target card {target_id} does not exist.")

        # Accept newly extended semantic link types
        # Validate that link_type is a valid link relation
        supported_links = {"PARENT", "RELATED", "SUPERSEDES", "DEPENDS_ON", "PREVENTS", "ENHANCES", "PROPOSES_UPDATE_TO", "DERIVED_FROM", "RELATED_TO", "REPLACES", "CONFLICTS_WITH", "IMPLEMENTS", "VALIDATES"}
        if link_type not in supported_links:
            raise ValueError(f"Unsupported link type: {link_type}")

        if link_type == "PARENT":
            if target_id not in source_card.parent_card_ids:
                source_card.parent_card_ids.append(target_id)
        elif link_type == "RELATED":
            if target_id not in source_card.related_card_ids:
                source_card.related_card_ids.append(target_id)
        else:
            # Custom linking relations stored inside extra_metadata for backward-compatible models
            if "links" not in source_card.extra_metadata:
                source_card.extra_metadata["links"] = []
            link_record = {"target_id": target_id, "link_type": link_type}
            if link_record not in source_card.extra_metadata["links"]:
                source_card.extra_metadata["links"].append(link_record)

        self.db_manager.store_card(source_card, updater=updater, reason=reason or f"Linked to {target_id} via {link_type}")

    def get_related_cards(self, card_id: str) -> List[KnowledgeCard]:
        """Retrieves linked parent, related, and other semantic cards of a given card."""
        card = self.get_card(card_id)
        if not card:
            return []
        related = []
        seen = set()

        for p_id in card.parent_card_ids:
            if p_id not in seen:
                p_card = self.get_card(p_id)
                if p_card:
                    related.append(p_card)
                    seen.add(p_id)

        for r_id in card.related_card_ids:
            if r_id not in seen:
                r_card = self.get_card(r_id)
                if r_card:
                    related.append(r_card)
                    seen.add(r_id)

        # Retrieve custom link targets as well
        custom_links = card.extra_metadata.get("links", [])
        for link in custom_links:
            target_id = link.get("target_id")
            if target_id and target_id not in seen:
                t_card = self.get_card(target_id)
                if t_card:
                    related.append(t_card)
                    seen.add(target_id)

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
        """Returns all cards associated with a given source ID."""
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
        Performs hybrid semantic-lexical search with weighted scoring.
        Calculates lexical scores (keywords) and dense cosine similarity scores.
        """
        all_cards = self.list_cards()
        ranked_results = []

        # Tokenize query for lexical search
        terms = [t.lower() for t in re.findall(r'\w+', query)] if query else []

        # Generate query embedding
        query_vector = self.embedder.get_embedding(query) if query else None


        import math
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc)

        for card in all_cards:
            if card_type and card.card_type.upper() != card_type.upper():
                continue
            if tags and not any(t.lower() in [ct.lower() for ct in card.tags] for t in tags):
                continue
            if security_classification and card.security_classification != security_classification:
                continue

            lexical_score = 0.0
            semantic_score = 0.0
            explanations = []

            # 1. Lexical Matching
            if terms:
                title_matches = 0
                summary_matches = 0
                body_matches = 0
                tag_matches = 0
                rationale_matches = 0

                for term in terms:
                    count = card.title.lower().count(term)
                    if count > 0:
                        title_matches += count
                        lexical_score += count * 10.0
                if title_matches:
                    explanations.append(f"Lexical Title matches ({title_matches}x, +{title_matches * 10:.1f} pts)")

                for term in terms:
                    count = card.summary.lower().count(term)
                    if count > 0:
                        summary_matches += count
                        lexical_score += count * 5.0
                if summary_matches:
                    explanations.append(f"Lexical Summary matches ({summary_matches}x, +{summary_matches * 5:.1f} pts)")

                for term in terms:
                    count = card.body.lower().count(term)
                    if count > 0:
                        body_matches += count
                        lexical_score += count * 2.0
                if body_matches:
                    explanations.append(f"Lexical Body matches ({body_matches}x, +{body_matches * 2:.1f} pts)")

                for term in terms:
                    for tag in card.tags:
                        if term in tag.lower():
                            tag_matches += 1
                            lexical_score += 8.0
                if tag_matches:
                    explanations.append(f"Lexical Tags matches ({tag_matches}x, +{tag_matches * 8:.1f} pts)")

                for term in terms:
                    for field_val in [card.why_created, card.problem_solved, card.future_work_dependent]:
                        count = field_val.lower().count(term)
                        if count > 0:
                            rationale_matches += count
                            lexical_score += count * 6.0
                if rationale_matches:
                    explanations.append(f"Lexical Rationale matches ({rationale_matches}x, +{rationale_matches * 6:.1f} pts)")

            # 2. Semantic Embedding Matching
            card_vector = card.extra_metadata.get("embedding")
            if query_vector and card_vector:
                similarity = self.embedder.cosine_similarity(query_vector, card_vector)
                # Map negative similarity to 0.0, keep range [0.0, 1.0]
                semantic_score = max(0.0, similarity)
                explanations.append(f"Semantic similarity: {semantic_score:.3f} (+{semantic_score * 60.0:.1f} pts)")

            # Combine scores: 40% lexical + 60% semantic (where semantic is scaled to [0.0, 60.0])
            # If no query string is provided, use card confidence score
            if query:
                base_score = (lexical_score * 0.4) + (semantic_score * 60.0)
            else:
                base_score = card.confidence * 10.0
                explanations.append(f"Default confidence rank (+{base_score:.1f} pts)")            # Recency weighting
            try:
                updated = datetime.fromisoformat(card.updated_at.replace("Z", "+00:00"))
                days_old = max(0.0, (now_utc - updated).total_seconds() / 86400.0)
                # Exponential decay based on days old (half-life of ~90 days)
                recency_multiplier = 0.8 + (0.2 * math.exp(-days_old / 90.0))
            except Exception:
                recency_multiplier = 1.0

            # Factor confidence as a multiplier
            confidence_multiplier = 0.5 + (card.confidence * 0.5)
            final_score = base_score * confidence_multiplier * recency_multiplier

            if recency_multiplier != 1.0:
                explanations.append(f"Recency Multiplier: {recency_multiplier:.2f}")


            if query and final_score == 0.0:
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

        ranked_results.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
        return ranked_results
