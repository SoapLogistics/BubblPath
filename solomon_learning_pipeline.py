import os
import json
import time
import uuid
from typing import Dict, List, Any

class LearningPipeline:
    """
    The core perpetual learning pipeline for Solomon.
    Transforms raw browser observations into structured System of Knowledge (SOK) Memory Cards.

    Pipeline Stages:
    1. Browser Observation -> 2. Memory Card -> 3. Embedding (Mock) -> 4. Knowledge Graph Linking -> 5. Save
    """
    def __init__(self):
        self.db_file = "sok_memory_cards.json"
        self.memory_matrix: Dict[str, Dict] = self._load_db()

    def _load_db(self) -> Dict[str, Dict]:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_db(self):
        with open(self.db_file, "w") as f:
            json.dump(self.memory_matrix, f, indent=2)

    def _generate_card_id(self, domain: str) -> str:
        return f"SOK-{domain.upper()}-{int(time.time())}-{str(uuid.uuid4())[:4]}"

    def process_observation(self, context_payload: Dict[str, Any]) -> Dict:
        """
        Entry point for the Learning Pipeline.
        Takes a raw context payload from the Browser Extension and processes it into memory.
        """
        print(f"🧠 LEARNING PIPELINE: Processing observation from {context_payload.get('url')}")

        # Stage 1: Card Generation
        card = self._generate_memory_card(context_payload)

        # Stage 2: Mock Embedding Generation
        card = self._generate_embeddings(card)

        # Stage 3: Knowledge Graph Linking
        card = self._link_to_graph(card)

        # Stage 4: Skill Extraction & Procedure Generation
        card = self._extract_skills(card)

        # Stage 5: Execution Planner Review
        card = self._review_and_optimize(card)

        # Stage 6: Save & Reinforce
        self.memory_matrix[card["card_id"]] = card
        self._save_db()

        print(f"✅ LEARNING PIPELINE: Successfully committed {card['card_id']} to Mnemosyne Matrix.")
        return card

    def _extract_skills(self, card: Dict) -> Dict:
        """Mock: Extracts reusable skills or procedures from the memory card."""
        card["extracted_skills"] = []
        if "github" in card["domain_type"]:
            card["extracted_skills"].append({"skill": "Git Merge Resolution", "confidence": 0.6})
        elif "ecommerce" in card["semantic_tags"]:
            card["extracted_skills"].append({"skill": "Price Comparison", "confidence": 0.9})
        return card

    def _review_and_optimize(self, card: Dict) -> Dict:
        """Mock: Reviews the generated card and optimizes its tags/confidence."""
        if len(card["summary"]) > 100:
            card["confidence_score"] += 0.05
        return card

    def _generate_memory_card(self, payload: Dict[str, Any]) -> Dict:
        """Converts ephemeral browser context into a structured SOK Node."""
        domain_type = payload.get('type', 'generic')
        title = payload.get('title', 'Unknown Title')
        url = payload.get('url', 'unknown')
        raw_data = payload.get('data', '')

        # Super-simple summarization heuristic for the mock
        summary = raw_data[:200] + "..." if len(raw_data) > 200 else raw_data

        card = {
            "card_id": self._generate_card_id(domain_type),
            "timestamp": time.time(),
            "source_url": url,
            "domain_type": domain_type,
            "title": title,
            "summary": summary,
            "raw_data_length": len(raw_data),
            "semantic_tags": [domain_type],
            "embeddings": [],
            "graph_links": [],
            "confidence_score": 0.85 # Initial trust score
        }

        # Domain-specific tagging
        if "github" in domain_type:
            card["semantic_tags"].extend(["code", "repository", "pull_request"])
        elif "amazon" in domain_type or "ebay" in domain_type:
            card["semantic_tags"].extend(["ecommerce", "pricing", "product"])
        elif "draftkings" in domain_type or "kalshi" in domain_type:
            card["semantic_tags"].extend(["prediction_market", "odds", "finance"])

        return card

    def _generate_embeddings(self, card: Dict) -> Dict:
        """Mock: Generates a dense vector embedding for semantic search."""
        # In production, this calls OpenAI or a local huggingface model
        card["embeddings"] = [round(time.time() % 1, 4), 0.5, 0.1] # Dummy vector
        return card

    def _link_to_graph(self, card: Dict) -> Dict:
        """Mock: Links the new card to existing concepts in the Knowledge Graph."""
        # E.g., if this is an Amazon GPU page, link it to the core 'GPU' concept node.
        # For this prototype, we'll just link it to the previous card if it exists.
        if len(self.memory_matrix) > 0:
            last_card_id = list(self.memory_matrix.keys())[-1]
            card["graph_links"].append({
                "target_id": last_card_id,
                "relationship": "temporal_sequence",
                "weight": 0.5
            })
        return card

    def query_memory(self, query_tag: str) -> List[Dict]:
        """Simple retrieval function."""
        results = []
        for card in self.memory_matrix.values():
            if query_tag in card.get("semantic_tags", []):
                results.append(card)
        return results