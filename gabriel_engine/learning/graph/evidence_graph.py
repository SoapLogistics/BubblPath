from typing import Dict, Any, List

class EvidenceGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_evidence(self, evidence: Dict[str, Any]) -> str:
        evidence_id = f"EV-{len(self.nodes) + 1}"
        self.nodes[evidence_id] = evidence
        return evidence_id

    def get_related_evidence(self, pattern: str) -> List[Dict[str, Any]]:
        # Dummy correlation
        return [v for k, v in self.nodes.items() if pattern in str(v)]
