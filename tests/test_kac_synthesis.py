import pytest
from backend.services.kac.synthesis.synthesis_engine import SynthesisEngine

def test_synthesis_engine_conflict():
    se = SynthesisEngine()

    new_facts = [{"type": "fact", "content": "not X", "source": "book1"}]
    memory = [{"type": "fact", "content": "X", "source": "memory_atom1"}]

    consensus, conflicts, campaigns = se.synthesize_knowledge(new_facts, memory)

    assert len(conflicts) == 1
    assert len(campaigns) == 1
    assert "not X" in conflicts[0].claim_b.get("content")

def test_synthesis_engine_consensus():
    se = SynthesisEngine()

    new_facts = [{"type": "fact", "content": "Y", "source": "book2"}]
    memory = [{"type": "fact", "content": "Y", "source": "memory_atom2"}]

    consensus, conflicts, campaigns = se.synthesize_knowledge(new_facts, memory)

    assert len(consensus) == 1
    assert len(conflicts) == 0
    assert "y" in consensus[0].statement
