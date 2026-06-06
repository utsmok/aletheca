"""SynthecaClient — async client for the OpenAlex API."""

from typing import Self

from bibliofabric.auth import AuthStrategy, NoAuth, QueryParameterAuth
from bibliofabric.client import BaseApiClient
from bibliofabric.log_config import logger

from .config import SynthecaSettings, get_settings
from .constants import OPENALEX_API_BASE_URL
from .unwrapper import OpenAlexUnwrapper


class SynthecaClient(BaseApiClient):
    """Asynchronous client for the OpenAlex API.

    Provides access to all OpenAlex entity endpoints through typed resource
    client properties.

    Usage::

        async with SynthecaClient() as client:
            work = await client.works.get("W1234567890")
    """

    def __init__(
        self,
        settings: SynthecaSettings | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize the SynthecaClient.

        Args:
            settings: Optional SynthecaSettings instance. If None, loads from env.
            api_key: Optional OpenAlex API key (overrides settings).
            base_url: Optional API base URL override.
        """
        self._settings = settings or get_settings()
        resolved_api_key = api_key or self._settings.openalex_api_key
        resolved_base_url = base_url or OPENALEX_API_BASE_URL

        auth = self._resolve_auth(resolved_api_key)

        super().__init__(
            base_url=resolved_base_url,
            auth_strategy=auth,
            response_unwrapper=OpenAlexUnwrapper(),
            timeout=self._settings.timeout,
            max_retries=self._settings.max_retries,
            user_agent=self._settings.user_agent,
        )

        # Resource clients will be initialized lazily as properties
        self._works = None
        self._authors = None
        self._sources = None
        self._institutions = None
        self._topics = None
        self._keywords = None
        self._publishers = None
        self._funders = None

        logger.debug("SynthecaClient initialized successfully.")

    @staticmethod
    def _resolve_auth(api_key: str | None) -> AuthStrategy:
        """Resolve the authentication strategy.

        OpenAlex uses query-parameter auth (api_key), not header-based.
        """
        if api_key:
            return QueryParameterAuth(key_name="api_key", key_value=api_key)
        return NoAuth()

    # --- Resource client properties (lazy init) ---

    @property
    def works(self):
        """Access the Works endpoint client."""
        if self._works is None:
            from .resources import WorksClient

            self._works = WorksClient(self)
        return self._works

    @property
    def authors(self):
        """Access the Authors endpoint client."""
        if self._authors is None:
            from .resources import AuthorsClient

            self._authors = AuthorsClient(self)
        return self._authors

    @property
    def sources(self):
        """Access the Sources endpoint client."""
        if self._sources is None:
            from .resources import SourcesClient

            self._sources = SourcesClient(self)
        return self._sources

    @property
    def institutions(self):
        """Access the Institutions endpoint client."""
        if self._institutions is None:
            from .resources import InstitutionsClient

            self._institutions = InstitutionsClient(self)
        return self._institutions

    @property
    def topics(self):
        """Access the Topics endpoint client."""
        if self._topics is None:
            from .resources import TopicsClient

            self._topics = TopicsClient(self)
        return self._topics

    @property
    def keywords(self):
        """Access the Keywords endpoint client."""
        if self._keywords is None:
            from .resources import KeywordsClient

            self._keywords = KeywordsClient(self)
        return self._keywords

    @property
    def publishers(self):
        """Access the Publishers endpoint client."""
        if self._publishers is None:
            from .resources import PublishersClient

            self._publishers = PublishersClient(self)
        return self._publishers

    @property
    def funders(self):
        """Access the Funders endpoint client."""
        if self._funders is None:
            from .resources import FundersClient

            self._funders = FundersClient(self)
        return self._funders

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.aclose()
