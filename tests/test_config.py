"""Tests for syntheca.config — SynthecaSettings and get_settings."""

import pytest

from syntheca.config import SynthecaSettings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    """Clear the lru_cache on get_settings before and after every test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_settings():
    settings = SynthecaSettings()
    assert settings.openalex_api_key is None
    assert settings.user_agent.startswith("syntheca/")


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("SYNTHECA_OPENALEX_API_KEY", "env-key-123")
    settings = SynthecaSettings()
    assert settings.openalex_api_key == "env-key-123"


def test_settings_explicit_api_key():
    settings = SynthecaSettings(openalex_api_key="explicit-key")
    assert settings.openalex_api_key == "explicit-key"


def test_get_settings_cached():
    first = get_settings()
    second = get_settings()
    assert first is second


def test_settings_env_prefix():
    assert SynthecaSettings.model_config["env_prefix"] == "SYNTHECA_"
