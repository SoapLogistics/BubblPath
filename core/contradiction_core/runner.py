from typing import List, Tuple, Dict, Any
from .models import Claim, ContradictionEvidence, ResolutionPolicy, ContradictionCase
from .repository import ContradictionRepository
from .detector import detect, rank

class BatchRunner:
    def __init__(self, repository: ContradictionRepository, policy: ResolutionPolicy):
        self.repository = repository
        self.policy = policy

    def process_batch(self, records: List[Tuple[Claim, ContradictionEvidence]]) -> List[ContradictionCase]:
        """
        Processes a batch of records, detects contradictions without mutating memory,
        and saves cases to the repository.
        """
        cases = detect(records, self.policy)

        for case in cases:
            # We don't want to re-create or overwrite if we already processed this EXACT conflict
            # unless the severity/uncertainty changed, which `store_case` handles via upsert.
            self.repository.store_case(case)

        return rank(cases)

def generate_fixture_docket(repository: ContradictionRepository) -> List[ContradictionCase]:
    """
    Generates a realistic test docket of claims demonstrating all contradiction types.
    Does not interact with the rest of Solomon or memory, purely local test fixture.
    """
    from .models import ClaimScope

    policy = ResolutionPolicy(numerical_tolerance=0.05)
    runner = BatchRunner(repository, policy)

    claims_and_evidence = [
        # Direct Contradiction
        (
            Claim("c1", "earth", "shape", "flat"),
            ContradictionEvidence("srcA", 0.9, "2024-01-01T00:00:00Z", 0.5)
        ),
        (
            Claim("c2", "earth", "shape", "oblate spheroid"),
            ContradictionEvidence("srcB", 0.99, "2024-01-02T00:00:00Z", 0.95)
        ),

        # Temporal Contradiction (same entity, different time)
        (
            Claim("c3", "solomon", "status", "offline", scope=ClaimScope(start_time="2023-01-01T00:00:00Z", end_time="2023-12-31T23:59:59Z")),
            ContradictionEvidence("srcC", 1.0, "2024-01-01T00:00:00Z", 0.9)
        ),
        (
            Claim("c4", "solomon", "status", "online", scope=ClaimScope(start_time="2024-01-01T00:00:00Z")),
            ContradictionEvidence("srcC", 1.0, "2024-01-02T00:00:00Z", 0.9)
        ),

        # Numerical tolerance (non-conflict)
        (
            Claim("c5", "pi", "value", "3.14", unit="rad"),
            ContradictionEvidence("srcD", 0.8, "2024-01-01T00:00:00Z", 0.7)
        ),
        (
            Claim("c6", "pi", "value", "3.14159", unit="rad"),
            ContradictionEvidence("srcE", 0.9, "2024-01-01T00:00:00Z", 0.8)
        ),

        # Numerical contradiction (outside tolerance)
        (
            Claim("c7", "speed_of_light", "value", "300000", unit="km/s"),
            ContradictionEvidence("srcF", 0.8, "2024-01-01T00:00:00Z", 0.8)
        ),
        (
            Claim("c8", "speed_of_light", "value", "400000", unit="km/s"),
            ContradictionEvidence("srcG", 0.6, "2024-01-01T00:00:00Z", 0.6)
        ),

        # Scoped contradiction (different context)
        (
            Claim("c9", "apple", "color", "red", scope=ClaimScope(context="fuji")),
            ContradictionEvidence("srcH", 0.9, "2024-01-01T00:00:00Z", 0.8)
        ),
        (
            Claim("c10", "apple", "color", "green", scope=ClaimScope(context="granny smith")),
            ContradictionEvidence("srcI", 0.9, "2024-01-01T00:00:00Z", 0.8)
        ),
    ]

    return runner.process_batch(claims_and_evidence)
