"""Syntheca-specific settings for the OpenAlex API client."""

from functools import lru_cache

from bibliofabric.config import BaseApiSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .constants import DEFAULT_USER_AGENT


class SynthecaSettings(BaseApiSettings):
    """OpenAlex-specific settings.

    Inherits all generic API client settings from BaseApiSettings and adds
    OpenAlex-specific configuration.

    Settings are loaded from environment variables (prefixed with 'SYNTHECA_')
    or .env/secrets.env files.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "secrets.env"),
        env_file_encoding="utf-8",
        env_prefix="SYNTHECA_",
        extra="ignore",
        case_sensitive=False,
        arbitrary_types_allowed=True,
    )

    user_agent: str = Field(
        default=DEFAULT_USER_AGENT,
        description="User-Agent header for requests",
    )

    openalex_api_key: str | None = Field(
        default=None,
        description="OpenAlex API key for the polite pool",
    )


@lru_cache
def get_settings() -> SynthecaSettings:
    """Provide cached access to application settings."""
    return SynthecaSettings()
