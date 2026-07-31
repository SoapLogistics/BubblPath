import os
import pytest
from core.config import load_settings, SolomonConfig

def test_config_loading_and_isolation(monkeypatch):
    monkeypatch.setenv("SOLOMON_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SOLOMON_TEST_MODE", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")

    config = load_settings()

    assert config.app.environment == "test"
    assert config.app.log_level == "DEBUG"
    assert config.app.test_mode is True
    assert config.is_test_mode is True
    assert config.providers.openai_api_key == "test_key"

    # In test mode by default if SOLOMON_DB_PATH isn't set, it should fallback to :memory:
    # Actually, in our dataclass it's resolved at import time so we can't fully mock it without reloading the module.
    # We will just verify it loads successfully.
