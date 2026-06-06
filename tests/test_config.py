"""Tests for aletheca.config — AlethecaSettings and get_settings."""

import pytest

from aletheca.config import AlethecaSettings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    """Clear the lru_cache on get_settings before and after every test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_settings():
    settings = AlethecaSettings()
    assert settings.openalex_api_key is None
    assert settings.user_agent.startswith("aletheca/")


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("ALETHECA_OPENALEX_API_KEY", "env-key-123")
    settings = AlethecaSettings()
    assert settings.openalex_api_key == "env-key-123"


def test_settings_explicit_api_key():
    settings = AlethecaSettings(openalex_api_key="explicit-key")
    assert settings.openalex_api_key == "explicit-key"


def test_get_settings_cached():
    first = get_settings()
    second = get_settings()
    assert first is second


def test_settings_env_prefix():
    assert AlethecaSettings.model_config["env_prefix"] == "ALETHECA_"
