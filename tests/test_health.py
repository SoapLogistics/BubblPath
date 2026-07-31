import pytest
from datetime import datetime, UTC
from core.health import HealthRegistry, HealthStatus, HealthCheckResult

def test_registry_registration():
    registry = HealthRegistry()
    def check():
        return HealthCheckResult("test", HealthStatus.HEALTHY, datetime.now(UTC), "ok")

    registry.register("test", check)
    with pytest.raises(ValueError):
        registry.register("test", check)

def test_registry_status_calculation():
    registry = HealthRegistry()

    def healthy_check():
        return HealthCheckResult("s1", HealthStatus.HEALTHY, datetime.now(UTC), "ok")

    def degraded_check():
        return HealthCheckResult("s2", HealthStatus.DEGRADED, datetime.now(UTC), "degraded")

    def unhealthy_check():
        return HealthCheckResult("s3", HealthStatus.UNHEALTHY, datetime.now(UTC), "fail")

    registry.register("s1", healthy_check)
    res = registry.run_all()
    assert res["status"] == "healthy"

    registry.register("s2", degraded_check)
    res = registry.run_all()
    assert res["status"] == "degraded"

    registry.register("s3", unhealthy_check, critical=True)
    res = registry.run_all()
    assert res["status"] == "unhealthy"

def test_registry_exception_handling():
    registry = HealthRegistry()

    def crash_check():
        raise ValueError("simulated crash")

    registry.register("s1", crash_check, critical=False)
    res = registry.run_all()
    assert res["status"] == "unknown"
    assert res["results"][0]["message"] == "Check function crashed"
    assert res["results"][0]["details"]["error_type"] == "ValueError"
