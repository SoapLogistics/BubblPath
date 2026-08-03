from typing import Dict, Any, List
from gabriel_engine.learning.evidence.inventory_reader import InventoryReader
from gabriel_engine.learning.evidence.mission_reader import MissionReader
from gabriel_engine.learning.graph.evidence_graph import EvidenceGraph

class EvidenceExtractor:
    def __init__(self):
        self.inventory_reader = InventoryReader()
        self.mission_reader = MissionReader()
        self.graph = EvidenceGraph()

    def process_normalized_outcome(self, normalized_outcome: Dict[str, Any]) -> List[str]:
        """
        Routes the normalized outcome to the appropriate reader to extract evidence
        and adds it to the Evidence Graph. Returns a list of evidence IDs.
        """
        evidence_list = []
        event_type = normalized_outcome.get("event_type", "")

        # Route to specific readers based on event type heuristics
        if "inventory" in event_type.lower():
            evidence_list.extend(self.inventory_reader.read(normalized_outcome))
        elif "mission" in event_type.lower() or "assimilation" in event_type.lower():
            evidence_list.extend(self.mission_reader.read(normalized_outcome))
        else:
            # Generic fallback
            evidence_list.append({
                "type": "generic",
                "content": normalized_outcome,
                "confidence": 0.5
            })

        evidence_ids = []
        for evidence in evidence_list:
            ev_id = self.graph.add_evidence(evidence)
            evidence_ids.append(ev_id)

        return evidence_ids
