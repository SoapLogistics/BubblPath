from typing import List, Optional, Tuple, Dict, Any
from .models import Claim, ContradictionCase, ResolutionPolicy, ResolutionProposal
from .analyzer import analyze_pair, classify_contradiction, propose_resolutions
from .repository import ContradictionRepository

class ContradictionCoreAPI:
    def __init__(self, db_path: str = ":memory:"):
        self.repository = ContradictionRepository(db_path)

    def detect(self, records: List[Claim], policy: ResolutionPolicy) -> List[ContradictionCase]:
        """
        Compare all pairs of records to find contradictions.
        Saves cases to the repository and returns them.
        """
        cases = []
        n = len(records)
        for i in range(n):
            for j in range(i + 1, n):
                case = analyze_pair(records[i], records[j], policy)
                if case:
                    self.repository.save_case(case)
                    cases.append(case)
        return self.rank(cases)

    def classify(self, pair: Tuple[Claim, Claim], policy: ResolutionPolicy) -> Tuple[str, float]:
        """
        Classifies a pair directly. Returns (classification, severity).
        """
        return classify_contradiction(pair[0], pair[1], policy)

    def rank(self, cases: List[ContradictionCase]) -> List[ContradictionCase]:
        """
        Rank cases based on priority_score (descending) and severity.
        """
        return sorted(cases, key=lambda c: (c.priority_score, c.severity), reverse=True)

    def propose_resolution(self, case: ContradictionCase, policy: ResolutionPolicy) -> List[ResolutionProposal]:
        """
        Generates resolution proposals for an existing case based on the policy.
        """
        return propose_resolutions(case.classification, case.evidence.claim_a, case.evidence.claim_b, policy)

    def explain(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Provides a human/agent readable explanation table/summary of the contradiction.
        """
        case = self.repository.get_case(case_id)
        if not case:
            return None

        return {
            "case_id": case.id,
            "classification": case.classification,
            "status": case.status,
            "priority": case.priority_score,
            "evidence_comparison": {
                "claim_A": {
                    "id": case.evidence.claim_a.id,
                    "value": case.evidence.claim_a.value,
                    "source": case.evidence.claim_a.source_id,
                    "timestamp": case.evidence.claim_a.timestamp,
                    "confidence": case.evidence.claim_a.scope.confidence,
                    "domain": case.evidence.claim_a.scope.domain,
                },
                "claim_B": {
                    "id": case.evidence.claim_b.id,
                    "value": case.evidence.claim_b.value,
                    "source": case.evidence.claim_b.source_id,
                    "timestamp": case.evidence.claim_b.timestamp,
                    "confidence": case.evidence.claim_b.scope.confidence,
                    "domain": case.evidence.claim_b.scope.domain,
                }
            },
            "proposals": [
                {
                    "action": p.action,
                    "reason": p.reason_code,
                    "explanation": p.explanation,
                    "affected_claims": p.affected_claim_ids
                } for p in case.proposals
            ]
        }
