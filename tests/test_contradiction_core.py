import time
import pytest
from core.solomon_contradiction.models import Claim, ClaimScope, ResolutionPolicy
from core.solomon_contradiction.api import ContradictionCoreAPI

@pytest.fixture
def policy():
    return ResolutionPolicy(numerical_tolerance=0.05)

@pytest.fixture
def api():
    return ContradictionCoreAPI(db_path=":memory:")

def test_direct_contradiction(api, policy):
    claim_a = Claim(
        id="c1", entity="Project_X", predicate="status", value="ACTIVE",
        source_id="sys_1", timestamp=100.0, scope=ClaimScope(confidence=1.0)
    )
    claim_b = Claim(
        id="c2", entity="Project_X", predicate="status", value="CANCELLED",
        source_id="sys_2", timestamp=150.0, scope=ClaimScope(confidence=1.0)
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    case = cases[0]
    assert case.classification == "direct"
    assert case.severity == 1.0

    # Check proposal logic for recency
    assert any(p.action == "supersede" and "c1" in p.affected_claim_ids for p in case.proposals)

def test_temporal_contradiction(api, policy):
    claim_a = Claim(
        id="c1", entity="Stock_Price", predicate="value", value=150.0,
        source_id="sys_1", timestamp=100.0,
        scope=ClaimScope(start_time=100.0, end_time=200.0, confidence=1.0)
    )
    claim_b = Claim(
        id="c2", entity="Stock_Price", predicate="value", value=200.0,
        source_id="sys_2", timestamp=250.0,
        scope=ClaimScope(start_time=250.0, end_time=300.0, confidence=1.0)
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    case = cases[0]
    assert case.classification == "temporal"
    assert any(p.action == "retain-both-with-scope" for p in case.proposals)

def test_scoped_contradiction(api, policy):
    claim_a = Claim(
        id="c1", entity="Policy_Y", predicate="is_enabled", value=True,
        source_id="sys_1", timestamp=100.0,
        scope=ClaimScope(domain="US", confidence=1.0)
    )
    claim_b = Claim(
        id="c2", entity="Policy_Y", predicate="is_enabled", value=False,
        source_id="sys_2", timestamp=100.0,
        scope=ClaimScope(domain="EU", confidence=1.0)
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    case = cases[0]
    assert case.classification == "scoped"
    assert any(p.action == "retain-both-with-scope" for p in case.proposals)

def test_numerical_tolerance(api, policy):
    # Within 5% tolerance
    claim_a = Claim(
        id="c1", entity="Metric_Z", predicate="latency", value=100.0,
        source_id="sys_1", timestamp=100.0
    )
    claim_b = Claim(
        id="c2", entity="Metric_Z", predicate="latency", value=102.0,
        source_id="sys_2", timestamp=100.0
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 0  # Should be classified as apparent/non-conflict and ignored

    # Outside tolerance
    claim_c = Claim(
        id="c3", entity="Metric_Z", predicate="latency", value=110.0,
        source_id="sys_3", timestamp=100.0
    )
    cases2 = api.detect([claim_a, claim_c], policy)
    assert len(cases2) == 1
    assert cases2[0].classification == "numerical"

def test_definitional_contradiction(api, policy):
    claim_a = Claim(
        id="c1", entity="Distance", predicate="value", value="100 miles",
        source_id="sys_1", timestamp=100.0, qualifiers={"unit": "miles"}
    )
    claim_b = Claim(
        id="c2", entity="Distance", predicate="value", value="160 km",
        source_id="sys_2", timestamp=100.0, qualifiers={"unit": "km"}
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    assert cases[0].classification == "definitional"
    assert any(p.action == "merge-definitions" for p in cases[0].proposals)

def test_source_quality_contradiction(api, policy):
    claim_a = Claim(
        id="c1", entity="Data_X", predicate="value", value="A",
        source_id="low_tier", timestamp=100.0, scope=ClaimScope(confidence=0.4)
    )
    claim_b = Claim(
        id="c2", entity="Data_X", predicate="value", value="B",
        source_id="high_tier", timestamp=100.0, scope=ClaimScope(confidence=0.9)
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    assert cases[0].classification == "source-quality"
    assert any(p.action == "lower-confidence" and "c1" in p.affected_claim_ids for p in cases[0].proposals)

def test_duplicate_case_collapse(api, policy):
    claim_a = Claim(
        id="c1", entity="Val", predicate="is_true", value=True,
        source_id="sys_1", timestamp=100.0
    )
    claim_b = Claim(
        id="c2", entity="Val", predicate="is_true", value=False,
        source_id="sys_2", timestamp=100.0
    )

    api.detect([claim_a, claim_b], policy)
    api.detect([claim_a, claim_b], policy)  # Process same pair again

    # Repository should only have 1 case due to deterministic ID hashing
    saved_cases = api.repository.list_cases()
    assert len(saved_cases) == 1

def test_explain_endpoint(api, policy):
    claim_a = Claim(
        id="c1", entity="Val", predicate="is_true", value=True,
        source_id="sys_1", timestamp=100.0
    )
    claim_b = Claim(
        id="c2", entity="Val", predicate="is_true", value=False,
        source_id="sys_2", timestamp=100.0
    )

    cases = api.detect([claim_a, claim_b], policy)
    case_id = cases[0].id

    explanation = api.explain(case_id)
    assert explanation is not None
    assert explanation["classification"] == "direct"
    assert explanation["evidence_comparison"]["claim_A"]["value"] == True
    assert explanation["evidence_comparison"]["claim_B"]["value"] == False

def test_no_mutation(api, policy):
    # Ensure memory is NOT mutated - just returns cases and saves to intermediate case repo
    claim_a = Claim(
        id="c1", entity="Val", predicate="is_true", value=True,
        source_id="sys_1", timestamp=100.0
    )
    claim_b = Claim(
        id="c2", entity="Val", predicate="is_true", value=False,
        source_id="sys_2", timestamp=100.0
    )

    cases = api.detect([claim_a, claim_b], policy)
    assert len(cases) == 1
    assert claim_a.value == True
    assert claim_b.value == False
