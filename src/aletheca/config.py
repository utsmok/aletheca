"""Aletheca settings for the OpenAlex API client.

Loaded from environment variables prefixed with ``ALETHECA_`` and a ``.env``
file in the working directory.
"""

from functools import lru_cache
from typing import Literal

from bibliofabric.config import BaseApiSettings
from pydantic import AliasChoices, Field
from pydantic_settings import SettingsConfigDict

#: OpenAlex per-client request budget: 10-50 req/s by plan with lower caps for
#: boolean-heavy searches and semantic search; the safe general pace is 10.
DEFAULT_MAX_REQUESTS_PER_SECOND = 10.0
DEFAULT_MAX_CONCURRENCY = 5

AuthScheme = Literal["query", "bearer"]
"""How the API key is sent: ``query`` (``?api_key=...``, the default) or
``bearer`` (``Authorization: Bearer ...``, required for collections writes)."""


BASE_MAX_CONCURRENCY = 10
"""The BaseApiSettings default; replaced with the OpenAlex pace when unset."""


class AlethecaSettings(BaseApiSettings):
    """OpenAlex-specific client settings.

    Inherits ``timeout``, ``max_retries``, ``max_retry_wait``,
    ``max_requests_per_second``, ``max_concurrency``, ``user_agent`` and
    ``mailto`` from :class:`bibliofabric.config.BaseApiSettings` and adds the
    OpenAlex credential and auth-scheme fields.

    The polite pool no longer exists: since February 2026 OpenAlex ignores
    ``mailto`` and meteres unkeyed traffic at $0.10/day per IP. A free API key
    raises the budget to $1/day and is required for cursor paging beyond the
    first page. Get one at https://openalex.org/settings/api.
    """

    model_config = SettingsConfigDict(
        env_prefix="ALETHECA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("api_key", "openalex_api_key"),
        description="OpenAlex API key; env names ALETHECA_API_KEY and the "
        "consumer-legacy ALETHECA_OPENALEX_API_KEY both work.",
    )
    auth_scheme: AuthScheme = Field(
        default="query",
        description="Send the key as the ``api_key`` query parameter or as an "
        "``Authorization: Bearer`` header.",
    )
    # The conservative OpenAlex limiter defaults (D-15: 10 req/s, concurrency
    # 5) are applied by AlethecaClient when the base fields are unset; they
    # cannot be redeclared here because ty rejects mutable attribute
    # overrides of the base settings. Env overrides keep working.


@lru_cache
def get_settings() -> AlethecaSettings:
    """Return the process-wide settings, loaded once from the environment."""
    return AlethecaSettings()
