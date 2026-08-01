import os
import sqlite3
import pytest
from core.contradiction_core.models import (
    Claim, ClaimScope, ContradictionEvidence, ResolutionPolicy,
    ContradictionCase, ValidationError
)
from core.contradiction_core.repository import ContradictionRepository
from core.contradiction_core.detector import detect, classify, rank
from core.contradiction_core.runner import BatchRunner, generate_fixture_docket

def test_claim_validation():
    # Valid claim
    c = Claim("c1", "earth", "shape", "flat")
    assert c.entity == "earth"

    # Missing entity
    with pytest.raises(ValidationError):
        Claim("c1", "", "shape", "flat")

def test_claim_fingerprint():
    c1 = Claim("c1", "earth", "shape", "flat", unit="none")
    c2 = Claim("c2", "EARTH", "SHAPE", "FLAT", unit="NONE")
    assert c1.fingerprint() == c2.fingerprint()

def test_temporal_disjoint():
    s1 = ClaimScope(start_time="2024-01-01T00:00:00Z", end_time="2024-01-31T23:59:59Z")
    s2 = ClaimScope(start_time="2024-02-01T00:00:00Z", end_time="2024-02-28T23:59:59Z")
    s3 = ClaimScope(start_time="2024-01-15T00:00:00Z", end_time="2024-02-15T23:59:59Z")

    assert s1.is_disjoint_temporal(s2) is True
    assert s2.is_disjoint_temporal(s1) is True
    assert s1.is_disjoint_temporal(s3) is False

def test_classify_direct():
    c1 = Claim("c1", "earth", "shape", "flat")
    c2 = Claim("c2", "earth", "shape", "spherical")
    policy = ResolutionPolicy()
    assert classify(c1, c2, policy) == "DIRECT"

def test_classify_temporal():
    c1 = Claim("c1", "status", "system", "offline", scope=ClaimScope(start_time="2023-01-01T00:00:00Z", end_time="2023-12-31T23:59:59Z"))
    c2 = Claim("c2", "status", "system", "online", scope=ClaimScope(start_time="2024-01-01T00:00:00Z"))
    policy = ResolutionPolicy()
    assert classify(c1, c2, policy) == "TEMPORAL"

def test_classify_numerical():
    c1 = Claim("c1", "pi", "value", "3.14", unit="rad")
    c2 = Claim("c2", "pi", "value", "3.14159", unit="rad")
    c3 = Claim("c3", "pi", "value", "4.0", unit="rad")

    policy = ResolutionPolicy(numerical_tolerance=0.05)

    assert classify(c1, c2, policy) == "APPARENT_NON_CONFLICT"
    assert classify(c1, c3, policy) == "NUMERICAL"

def test_detect_and_rank():
    policy = ResolutionPolicy(numerical_tolerance=0.05)
    claims_and_evidence = [
        (Claim("c1", "a", "b", "c"), ContradictionEvidence("s1", 0.9, "2024-01-01T00:00:00Z", 0.9)),
        (Claim("c2", "a", "b", "d"), ContradictionEvidence("s2", 0.8, "2024-01-01T00:00:00Z", 0.8)),
    ]

    cases = detect(claims_and_evidence, policy)
    assert len(cases) == 1

    case = cases[0]
    assert case.classification == "DIRECT"
    assert case.severity > 0.5

    # proposals should be present
    assert len(case.proposals) > 0

def test_repository_persistence(tmp_path):
    db_path = str(tmp_path / "test_repo.db")
    repo = ContradictionRepository(db_path)

    c1 = Claim("c1", "x", "y", "z")
    c2 = Claim("c2", "x", "y", "w")
    e1 = ContradictionEvidence("s1", 1.0, "2024-01-01T00:00:00Z")
    e2 = ContradictionEvidence("s2", 1.0, "2024-01-01T00:00:00Z")

    case = ContradictionCase("case1", c1, c2, e1, e2, classification="DIRECT")
    repo.store_case(case)

    retrieved = repo.get_case("case1")
    assert retrieved is not None
    assert retrieved.case_id == "case1"
    assert retrieved.classification == "DIRECT"
    assert retrieved.claim1.entity == "x"

def test_fixture_docket(tmp_path):
    db_path = str(tmp_path / "fixture.db")
    repo = ContradictionRepository(db_path)
    cases = generate_fixture_docket(repo)

    assert len(cases) > 0
    # Should be sorted by severity descending
    assert cases[0].severity >= cases[-1].severity

    # Ensure they are saved
    saved_cases = repo.list_cases()
    assert len(saved_cases) == len(cases)
