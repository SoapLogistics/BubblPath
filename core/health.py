from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable, Callable, Dict, List

logger = logging.getLogger("solomon.health")

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class HealthCheckResult:
    service: str
    status: HealthStatus
    checked_at: datetime
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None

@runtime_checkable
class HealthCheckable(Protocol):
    def healthcheck(self) -> HealthCheckResult:
        ...

class HealthRegistry:
    def __init__(self):
        self._checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self._critical: Dict[str, bool] = {}

    def register(self, name: str, checker: Callable[[], HealthCheckResult], critical: bool = True):
        if name in self._checks:
            raise ValueError(f"Health check for '{name}' is already registered.")
        self._checks[name] = checker
        self._critical[name] = critical

    def run_all(self) -> Dict[str, Any]:
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, checker in self._checks.items():
            start = time.perf_counter()
            try:
                res = checker()
            except Exception as e:
                logger.exception(f"Health check failed to execute for {name}")
                res = HealthCheckResult(
                    service=name,
                    status=HealthStatus.UNKNOWN,
                    checked_at=datetime.now(UTC),
                    message="Check function crashed",
                    details={"error_type": type(e).__name__}
                )

            elapsed = (time.perf_counter() - start) * 1000

            # Reconstruct result to ensure latency is included
            final_res = HealthCheckResult(
                service=res.service,
                status=res.status,
                checked_at=res.checked_at,
                message=res.message,
                details=res.details,
                latency_ms=elapsed
            )
            results.append(final_res)

            is_critical = self._critical[name]

            if final_res.status == HealthStatus.UNHEALTHY:
                if is_critical:
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif final_res.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif final_res.status == HealthStatus.UNKNOWN:
                if overall_status != HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNKNOWN

        return {
            "status": overall_status.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": [
                {
                    "service": r.service,
                    "status": r.status.value,
                    "checked_at": r.checked_at.isoformat(),
                    "message": r.message,
                    "details": r.details,
                    "latency_ms": r.latency_ms
                }
                for r in results
            ]
        }

# Global registry
registry = HealthRegistry()
