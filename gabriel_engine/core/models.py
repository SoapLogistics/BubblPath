import datetime
from typing import Any


class AcquisitionRecord:
    def __init__(
        self,
        project_name: str,
        source_location: str,
        source_type: str,
        owner_authorization: str = "user_provided",
        license_detected: str = "Unknown",
        allowed_actions: list[str] | None = None,
        prohibited_actions: list[str] | None = None,
        timestamp: str | None = None,
        content_hash: str = "",
        aggressive_mode: bool = True
    ):
        self.project_name = project_name
        self.source_location = source_location
        self.source_type = source_type
        self.owner_authorization = owner_authorization
        self.license_detected = license_detected
        self.allowed_actions = allowed_actions or []
        self.prohibited_actions = prohibited_actions or []
        self.timestamp = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.content_hash = content_hash
        self.aggressive_mode = aggressive_mode

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "source_location": self.source_location,
            "source_type": self.source_type,
            "owner_authorization": self.owner_authorization,
            "license_detected": self.license_detected,
            "allowed_actions": self.allowed_actions,
            "prohibited_actions": self.prohibited_actions,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
            "aggressive_mode": self.aggressive_mode
        }


class ProgramAnatomyCard:
    def __init__(
        self,
        capability: str,
        inputs: list[str],
        outputs: list[str],
        core_mechanisms: list[str],
        valuable_patterns: list[str],
        solomon_relevance: list[str],
        languages: list[str] | None = None,
        dependencies: list[str] | None = None
    ):
        self.capability = capability
        self.inputs = inputs
        self.outputs = outputs
        self.core_mechanisms = core_mechanisms
        self.valuable_patterns = valuable_patterns
        self.solomon_relevance = solomon_relevance
        self.languages = languages or []
        self.dependencies = dependencies or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "core_mechanisms": self.core_mechanisms,
            "valuable_patterns": self.valuable_patterns,
            "solomon_relevance": self.solomon_relevance,
            "languages": self.languages,
            "dependencies": self.dependencies
        }


class CapabilityMemoryCard:
    def __init__(
        self,
        name: str,
        source_project: str,
        source_license: str,
        concept_summary: str,
        implementation_status: str = "independently_implemented",
        confidence: float = 1.0,
        tested_on: list[str] | None = None,
        result: dict[str, Any] | None = None,
        card_type: str = "capability_pattern"
    ):
        self.card_type = card_type
        self.name = name
        self.source_project = source_project
        self.source_license = source_license
        self.concept_summary = concept_summary
        self.implementation_status = implementation_status
        self.confidence = confidence
        self.tested_on = tested_on or []
        self.result = result or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_type": self.card_type,
            "name": self.name,
            "source_project": self.source_project,
            "source_license": self.source_license,
            "concept_summary": self.concept_summary,
            "implementation_status": self.implementation_status,
            "confidence": self.confidence,
            "tested_on": self.tested_on,
            "result": self.result
        }


class CrucibleReport:
    def __init__(
        self,
        baseline_metrics: dict[str, Any],
        capability_metrics: dict[str, Any],
        comparison_results: dict[str, Any],
        decision: str,
        notes: str = ""
    ):
        self.baseline_metrics = baseline_metrics
        self.capability_metrics = capability_metrics
        self.comparison_results = comparison_results
        self.decision = decision
        self.notes = notes

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_metrics": self.baseline_metrics,
            "capability_metrics": self.capability_metrics,
            "comparison_results": self.comparison_results,
            "decision": self.decision,
            "notes": self.notes
        }
