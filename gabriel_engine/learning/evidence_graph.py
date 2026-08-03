from typing import Dict, List
from gabriel_engine.learning.models import Evidence, Hypothesis

class EvidenceGraph:
    def __init__(self):
        self.evidence_nodes: Dict[str, Evidence] = {}
        self.hypothesis_nodes: Dict[str, Hypothesis] = {}
        # Mapping from hypothesis_id -> List of evidence_ids
        self.edges: Dict[str, List[str]] = {}

    def add_evidence(self, evidence: Evidence):
        self.evidence_nodes[evidence.id] = evidence

    def add_hypothesis(self, hypothesis: Hypothesis):
        self.hypothesis_nodes[hypothesis.id] = hypothesis
        if hypothesis.id not in self.edges:
            self.edges[hypothesis.id] = []

    def link(self, hypothesis_id: str, evidence_id: str):
        if hypothesis_id not in self.hypothesis_nodes:
            raise ValueError(f"Hypothesis {hypothesis_id} not in graph.")
        if evidence_id not in self.evidence_nodes:
            raise ValueError(f"Evidence {evidence_id} not in graph.")

        if hypothesis_id not in self.edges:
            self.edges[hypothesis_id] = []
        if evidence_id not in self.edges[hypothesis_id]:
            self.edges[hypothesis_id].append(evidence_id)
            # Update the underlying Pydantic model
            if evidence_id not in self.hypothesis_nodes[hypothesis_id].evidence_ids:
                self.hypothesis_nodes[hypothesis_id].evidence_ids.append(evidence_id)

    def get_evidence_for_hypothesis(self, hypothesis_id: str) -> List[Evidence]:
        if hypothesis_id not in self.edges:
            return []
        return [self.evidence_nodes[e_id] for e_id in self.edges[hypothesis_id]]
