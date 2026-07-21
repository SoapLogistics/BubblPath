import re
import math
from typing import List, Dict, Any, Optional
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.models.card import KnowledgeCard

class CardRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_card(self, card: KnowledgeCard, creator: str = "system", reason: Optional[str] = None) -> None:
        """Creates a new card in the storage layer."""
        self.db_manager.store_card(card, updater=creator, reason=reason or "Initial creation")

    def get_card(self, card_id: str) -> Optional[KnowledgeCard]:
        """Reads a card by ID."""
        return self.db_manager.get_card(card_id)

    def update_card(self, card: KnowledgeCard, updater: str = "system", reason: Optional[str] = None) -> None:
        """Updates an existing card in the database, appending to revision history."""
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

    def _tokenize(self, text: str) -> List[str]:
        """Utility method to safely normalize and tokenize text into words."""
        return [w.lower() for w in re.findall(r'\w+', text or "")]

    def _compute_cosine_similarity(self, query_tokens: List[str], doc_tokens: List[str], all_docs_tokens: List[List[str]]) -> float:
        """Calculates lightweight cosine similarity between query and doc using TF-IDF."""
        if not query_tokens or not doc_tokens:
            return 0.0

        # Term frequency for query & doc
        query_tf = {}
        for token in query_tokens:
            query_tf[token] = query_tf.get(token, 0) + 1

        doc_tf = {}
        for token in doc_tokens:
            doc_tf[token] = doc_tf.get(token, 0) + 1

        # Inverse document frequency
        total_docs = len(all_docs_tokens)
        vocabulary = set(query_tokens).union(set(doc_tokens))
        idf = {}
        for term in vocabulary:
            matching_docs = sum(1 for dt in all_docs_tokens if term in dt)
            # Standard smooth idf formula
            idf[term] = math.log((1 + total_docs) / (1 + matching_docs)) + 1.0

        # Compute query vector
        query_vec = {}
        query_mag = 0.0
        for term, tf in query_tf.items():
            val = tf * idf.get(term, 1.0)
            query_vec[term] = val
            query_mag += val * val
        query_mag = math.sqrt(query_mag)

        # Compute doc vector
        doc_vec = {}
        doc_mag = 0.0
        for term, tf in doc_tf.items():
            val = tf * idf.get(term, 1.0)
            doc_vec[term] = val
            doc_mag += val * val
        doc_mag = math.sqrt(doc_mag)

        if query_mag == 0.0 or doc_mag == 0.0:
            return 0.0

        # Calculate dot product
        dot_product = sum(query_vec.get(t, 0.0) * doc_vec.get(t, 0.0) for t in query_tokens if t in doc_vec)
        return dot_product / (query_mag * doc_mag)

    def search(
        self,
        query: str,
        card_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_classification: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid keyword-based lexical and TF-IDF semantic vector search with weighted ranking.
        Query terms are matched against title, summary, body, tags, and 'why_created', 'problem_solved'.
        """
        all_cards = self.list_cards()
        ranked_results = []

        # Tokenize query
        terms = self._tokenize(query)

        # Build vocabulary for the entire memory corpus
        all_docs_tokens = []
        for card in all_cards:
            full_text = f"{card.title} {card.summary} {card.body} {' '.join(card.tags)} {card.why_created} {card.problem_solved}"
            all_docs_tokens.append(self._tokenize(full_text))

        for idx, card in enumerate(all_cards):
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

            # 1. Lexical FTS matching and scoring
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

                # 2. Semantic vector cosine similarity scoring
                doc_tokens = all_docs_tokens[idx]
                cosine_sim = self._compute_cosine_similarity(terms, doc_tokens, all_docs_tokens)
                if cosine_sim > 0.0:
                    # Semantic scale matches roughly 0-10pts
                    semantic_boost = cosine_sim * 15.0
                    score += semantic_boost
                    explanations.append(f"Semantic Cosine Boost (+{semantic_boost:.2f} pts, similarity: {cosine_sim:.3f})")
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
