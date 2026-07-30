import pytest
import numpy as np
from solomon_quantized_memory import QuantizedBrainMap, QuantizedMemoryNode
from services.solomon_futures_engine import Candidate, FuturesEngine
from core.solomon_knowledge_cards.planner.models import TaskPlan

def test_memory_duplication_prevention():
    """Verify that Mnemosyne prevents duplicate memory ingestion."""
    brain = QuantizedBrainMap()

    id1 = brain.ingest(node_type="test_fact", content="Prussian blue is a synthetic pigment.")
    id2 = brain.ingest(node_type="test_fact", content="Prussian blue is a synthetic pigment.")

    assert id1 == id2
    assert len(brain.nodes) == 1

def test_memory_contradiction_detection(capsys):
    """Verify that Mnemosyne detects and flags contradictory memories."""
    brain = QuantizedBrainMap()

    # Ingest a highly positive memory
    id1 = brain.ingest(node_type="test_fact", content="The node operation succeeded.", valence=0.8)

    # Force similar embedding for contradiction test by copying or using similar properties
    node1 = brain.nodes[brain.id_map[id1]]
    # Fill with 1s to ensure dot product similarity is 1.0 (preventing sparse zero elements from lowering similarity)
    node1.ternary_vector = np.ones(128, dtype=np.int8)

    # Ingest a contradicting memory (opposite valence) with mocked identical ternary vector using a pure python init patch
    import unittest.mock
    from solomon_quantized_memory import QuantizedMemoryNode
    original_init = QuantizedMemoryNode.__init__
    def mock_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.ternary_vector = node1.ternary_vector

    with unittest.mock.patch.object(QuantizedMemoryNode, '__init__', mock_init):
        id2 = brain.ingest(node_type="test_fact_contradict", content="The node operation failed completely.", valence=-0.8)

    captured = capsys.readouterr()
    # It prints contradiction messages to stdout
    assert "CONTRADICTION DETECTED" in captured.out

def test_plan_constraints_step_limits():
    """Verify that planner rejects plans exceeding MAX_STEPS = 50 limit."""
    steps = [{"action": f"Step Action {i}"} for i in range(51)]

    plan = TaskPlan(
        plan_id="PLN-TEST-1",
        task_id="TSK-TEST-1",
        objective="Analyze planetary movement",
        steps=steps,
        retrieved_memory_card_ids=[],
        injected_safeguards=[]
    )

    with pytest.raises(ValueError) as excinfo:
        plan.validate()
    assert "exceeds maximum allowed steps limit" in str(excinfo.value)

def test_plan_constraints_loop_detection():
    """Verify that repeated/identical action steps trigger loop detection errors."""
    steps = [
        {"action": "Check directory status"},
        {"action": "Deploy web server"},
        {"action": "Check directory status"} # Repeated step
    ]

    plan = TaskPlan(
        plan_id="PLN-TEST-2",
        task_id="TSK-TEST-2",
        objective="Deploy standard web environment",
        steps=steps,
        retrieved_memory_card_ids=[],
        injected_safeguards=[]
    )

    with pytest.raises(ValueError) as excinfo:
        plan.validate()
    assert "Plan loop detected" in str(excinfo.value)

def test_plan_constraints_safety_validation():
    """Verify that dangerous executable actions are blocked and rejected."""
    steps = [
        {"action": "Check user profile"},
        {"action": "Run sudo rm -rf /etc/hosts"} # Dangerous step
    ]

    plan = TaskPlan(
        plan_id="PLN-TEST-3",
        task_id="TSK-TEST-3",
        objective="Fix local network configurations",
        steps=steps,
        retrieved_memory_card_ids=[],
        injected_safeguards=[]
    )

    with pytest.raises(ValueError) as excinfo:
        plan.validate()
    assert "Unsafe plan" in str(excinfo.value)

def test_simulation_input_boundaries():
    """Verify Candidate validate() strictly rejects out-of-bounds features."""
    # 1. Invalid baseline probability
    c_bad_prob = Candidate(
        candidate_id="c_err", event_id="e_err", domain="test", source_name="src",
        source_record_id="rec_err", source_mode="SHADOW", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=95.0, data_quality_score=95.0,
        features={"base_prob": 1.5} # Invalid base_prob > 1.0
    )
    errors = c_bad_prob.validate()
    assert "OUT_OF_BOUNDS_BASE_PROB" in errors

    # 2. Invalid volatility parameter
    c_bad_vol = Candidate(
        candidate_id="c_err2", event_id="e_err2", domain="test", source_name="src",
        source_record_id="rec_err2", source_mode="SHADOW", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=95.0, data_quality_score=95.0,
        features={"volatility_index": -0.5} # Invalid volatility < 0.0
    )
    errors2 = c_bad_vol.validate()
    assert "OUT_OF_BOUNDS_VOLATILITY_INDEX" in errors2

    # 3. Invalid source mode
    c_bad_mode = Candidate(
        candidate_id="c_err3", event_id="e_err3", domain="test", source_name="src",
        source_record_id="rec_err3", source_mode="DANGEROUS", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=95.0, data_quality_score=95.0,
        features={}
    )
    errors3 = c_bad_mode.validate()
    assert "INVALID_SOURCE_MODE" in errors3
