from .models import (
    Claim, ClaimScope, ContradictionEvidence, ResolutionProposal,
    ContradictionCase, ResolutionPolicy, CLASSIFICATION_TYPES,
    RESOLUTION_ACTIONS, ValidationError
)
from .repository import ContradictionRepository
from .detector import detect, classify, rank, propose_resolution, explain

__all__ = [
    "Claim",
    "ClaimScope",
    "ContradictionEvidence",
    "ResolutionProposal",
    "ContradictionCase",
    "ResolutionPolicy",
    "CLASSIFICATION_TYPES",
    "RESOLUTION_ACTIONS",
    "ValidationError",
    "ContradictionRepository",
    "detect",
    "classify",
    "rank",
    "propose_resolution",
    "explain"
]
