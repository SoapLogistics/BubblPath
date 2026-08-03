from gabriel_engine.learning.models import Evidence, Hypothesis, LearningRecord
from gabriel_engine.learning.evidence_graph import EvidenceGraph
from gabriel_engine.learning.pipeline import GabrielLearningPipeline

def test_evidence_graph_linking():
    graph = EvidenceGraph()
    ev1 = Evidence(id="e1", source_id="s1", content="test1", confidence=0.8)
    ev2 = Evidence(id="e2", source_id="s2", content="test2", confidence=0.9)
    hyp = Hypothesis(id="h1", description="test hyp", evidence_ids=[])

    graph.add_evidence(ev1)
    graph.add_evidence(ev2)
    graph.add_hypothesis(hyp)

    graph.link("h1", "e1")
    graph.link("h1", "e2")

    evidence_list = graph.get_evidence_for_hypothesis("h1")
    assert len(evidence_list) == 2
    assert "e1" in hyp.evidence_ids
    assert "e2" in hyp.evidence_ids
    assert evidence_list[0].content == "test1"

def test_pipeline_generates_learning_record():
    pipeline = GabrielLearningPipeline()
    result_dict = {
        "project_name": "TestProject",
        "compliance_lane": "GREEN",
        "capabilities_assimilated": [
            {
                "name": "TestCapability",
                "concept_summary": "Does a test.",
                "confidence": 0.95
            }
        ],
        "loop_learning_summary": {
            "execution_time": 1.2
        }
    }

    lr = pipeline.process_assimilation_result(result_dict)

    assert isinstance(lr, LearningRecord)
    assert lr.id.startswith("lr-")
    assert len(lr.observations) == 1
    assert lr.observations[0].event_type == "assimilation_loop_completion"

    assert len(lr.evidence) == 1
    assert lr.evidence[0].source_id == "TestCapability"
    assert lr.evidence[0].confidence == 0.95

    assert len(lr.hypotheses) == 1
    assert len(lr.validations) == 1
    assert lr.confidence == 0.95
