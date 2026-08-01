import sys
import time
from core.solomon_contradiction.models import Claim, ClaimScope, ResolutionPolicy
from core.solomon_contradiction.api import ContradictionCoreAPI

def generate_mock_claims():
    return [
        Claim(
            id="c1", entity="Project_Apollo", predicate="budget", value=1000000.0,
            source_id="finance_system_A", timestamp=time.time() - 86400,
            scope=ClaimScope(confidence=0.9, domain="SpaceX_Finance")
        ),
        Claim(
            id="c2", entity="Project_Apollo", predicate="budget", value=1100000.0,
            source_id="finance_system_B", timestamp=time.time(),
            scope=ClaimScope(confidence=0.95, domain="SpaceX_Finance")
        ),
        Claim(
            id="c3", entity="Module_X", predicate="status", value="ACTIVE",
            source_id="sys_1", timestamp=100.0,
            scope=ClaimScope(start_time=100.0, end_time=200.0, confidence=1.0)
        ),
        Claim(
            id="c4", entity="Module_X", predicate="status", value="DEPRECATED",
            source_id="sys_2", timestamp=250.0,
            scope=ClaimScope(start_time=250.0, end_time=300.0, confidence=1.0)
        )
    ]

def main():
    print("Initializing Contradiction Core (In-Memory)...")
    api = ContradictionCoreAPI(":memory:")
    policy = ResolutionPolicy(numerical_tolerance=0.05)

    claims = generate_mock_claims()
    print(f"Generated {len(claims)} mock claims.")

    print("Running detection batch...")
    cases = api.detect(claims, policy)

    print(f"\nDetected {len(cases)} contradiction cases.")
    for i, case in enumerate(cases):
        print(f"\n--- Case {i+1} ---")
        explanation = api.explain(case.id)
        print(f"Classification: {explanation['classification']}")
        print(f"Priority Score: {explanation['priority']:.2f}")
        print("Evidence:")
        print(f"  Claim A: {explanation['evidence_comparison']['claim_A']['id']} -> {explanation['evidence_comparison']['claim_A']['value']}")
        print(f"  Claim B: {explanation['evidence_comparison']['claim_B']['id']} -> {explanation['evidence_comparison']['claim_B']['value']}")
        print("Proposals:")
        for p in explanation['proposals']:
            print(f"  - [{p['action']}] {p['reason']} (Affects: {p['affected_claims']})")
            print(f"    Explanation: {p['explanation']}")

if __name__ == "__main__":
    main()
