import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

@dataclass(frozen=True)
class AppSettings:
    environment: str = field(default_factory=lambda: os.environ.get("SOLOMON_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))
    test_mode: bool = field(default_factory=lambda: os.environ.get("SOLOMON_TEST_MODE", "").lower() in ("true", "1", "yes"))

@dataclass(frozen=True)
class DatabaseSettings:
    db_path: Path = field(default_factory=lambda: Path(os.environ.get("SOLOMON_DB_PATH", ":memory:" if os.environ.get("SOLOMON_TEST_MODE", "").lower() in ("true", "1", "yes") else "solomon_hyper_memory.db")))
    wal_mode: bool = field(default_factory=lambda: os.environ.get("SQLITE_WAL_MODE", "true").lower() in ("true", "1"))
    timeout: float = field(default_factory=lambda: float(os.environ.get("SQLITE_TIMEOUT", "10.0")))

@dataclass(frozen=True)
class HealthSettings:
    enabled: bool = field(default_factory=lambda: os.environ.get("HEALTH_CHECKS_ENABLED", "true").lower() in ("true", "1"))
    timeout_ms: int = field(default_factory=lambda: int(os.environ.get("HEALTH_CHECK_TIMEOUT_MS", "5000")))

@dataclass(frozen=True)
class ProviderSettings:
    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    ddg_max_results: int = field(default_factory=lambda: int(os.environ.get("DDG_MAX_RESULTS", "3")))

@dataclass(frozen=True)
class SolomonConfig:
    app: AppSettings = field(default_factory=AppSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    health: HealthSettings = field(default_factory=HealthSettings)
    providers: ProviderSettings = field(default_factory=ProviderSettings)

    @property
    def is_test_mode(self) -> bool:
        return self.app.test_mode

def load_settings() -> SolomonConfig:
    """Canonical entry point to load application settings safely."""
    return SolomonConfig()

# Global default config
settings = load_settings()
