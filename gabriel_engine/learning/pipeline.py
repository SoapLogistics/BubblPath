import uuid
from typing import Dict, Any

from gabriel_engine.learning.models import (
    LearningRecord,
    Observation,
    Evidence,
    Hypothesis,
    Validation
)
from gabriel_engine.learning.evidence_graph import EvidenceGraph

class GabrielLearningPipeline:
    def __init__(self):
        self.evidence_graph = EvidenceGraph()

    def process_assimilation_result(self, result_dict: Dict[str, Any]) -> LearningRecord:
        """
        Extracts observations and evidence from an assimilation loop result,
        constructs hypotheses, runs (simulated) validation, and returns a LearningRecord.
        """
        record_id = f"lr-{uuid.uuid4().hex[:8]}"
        project_name = result_dict.get("project_name", "unknown_project")

        # Create Observation
        obs = Observation(
            id=f"obs-{uuid.uuid4().hex[:8]}",
            event_type="assimilation_loop_completion",
            details={
                "project_name": project_name,
                "lane_assigned": result_dict.get("compliance_lane", ""),
                "capabilities_assimilated_count": len(result_dict.get("capabilities_assimilated", [])),
                "loop_learning_summary": result_dict.get("loop_learning_summary", {})
            }
        )

        # Create Evidence from assimilated capabilities
        evidence_list = []
        for cap in result_dict.get("capabilities_assimilated", []):
            ev = Evidence(
                id=f"ev-{uuid.uuid4().hex[:8]}",
                source_id=cap.get("name", "unknown_capability"),
                content=f"Extracted capability: {cap.get('concept_summary', '')}",
                confidence=cap.get("confidence", 0.5)
            )
            evidence_list.append(ev)
            self.evidence_graph.add_evidence(ev)

        # Formulate Hypothesis
        hyp = Hypothesis(
            id=f"hyp-{uuid.uuid4().hex[:8]}",
            description=f"Capabilities assimilated from {project_name} enhance system utility.",
            evidence_ids=[]
        )
        self.evidence_graph.add_hypothesis(hyp)
        for ev in evidence_list:
            self.evidence_graph.link(hyp.id, ev.id)

        # Create Validation
        val = Validation(
            id=f"val-{uuid.uuid4().hex[:8]}",
            hypothesis_id=hyp.id,
            result="PROVISIONALLY_VALIDATED",
            metrics={"evidence_count": len(evidence_list)}
        )

        confidence_score = 0.0
        if evidence_list:
            confidence_score = sum(e.confidence for e in evidence_list) / len(evidence_list)

        lr = LearningRecord(
            id=record_id,
            observations=[obs],
            evidence=evidence_list,
            hypotheses=[hyp],
            validations=[val],
            confidence=confidence_score
        )

        return lr
