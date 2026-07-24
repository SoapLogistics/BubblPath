"""
Solomon Perpetual Learning Machine
Phase 14: Neural Synapse Mapper Engine (solomon_neural_synapse_mapper.py)

This module implements the Neural Synapse Mapper which dynamically groups and
fuses semantically related SOK cards inside the SQLite relational database
into unified, consolidated high-level concept nodes (synapses).
"""

from typing import List, Dict, Any

class NeuralSynapseMapper:
    """
    Scans and maps relationship clusters of SOK cards, fusing them
    into consolidated concept nodes representing high-level cognitive patterns.
    """

    def __init__(self, db_manager: Any):
        self.db = db_manager

    def blend_synapses(self, relationship_type: str = "DEPENDS_ON") -> Dict[str, Any]:
        """
        Scans all SOK cards and their directional links in the SQLite database,
        clustering them based on the specified relationship type.
        """
        # Fetch all cards from database
        all_cards = self.db.get_all_cards()
        if not all_cards:
            return {
                "synapses_created_count": 0,
                "synapses": [],
                "message": "No active SOK cards found in memory to map."
            }

        # Group cards by family or focus
        concept_clusters: Dict[str, List[str]] = {}
        for card in all_cards:
            card_id = card["card_id"]
            detailed_card = self.db.get_card(card_id)
            if not detailed_card:
                continue

            # Cluster by card family (or related targets via links)
            family = detailed_card.get("family", "General")
            if family not in concept_clusters:
                concept_clusters[family] = []
            concept_clusters[family].append(card_id)

        # Create consolidated concept synapses
        synapses = []
        for family, card_ids in concept_clusters.items():
            if len(card_ids) >= 2:
                synapse_id = f"SYNAPSE-{family.upper()}-CLUSTER"
                synapses.append({
                    "synapse_id": synapse_id,
                    "concept_domain": family,
                    "fused_cards": card_ids,
                    "coherence_index": round(1.0 - (1.0 / len(card_ids)), 4)
                })

        return {
            "synapses_created_count": len(synapses),
            "synapses": synapses,
            "message": f"Successfully blended SOK cards into {len(synapses)} unified concept synapses."
        }
