"""AlethecaClient — the async client for the OpenAlex API."""

import logging
from collections.abc import Mapping
from functools import cached_property
from typing import Any

import httpx
from bibliofabric.auth import (
    AuthStrategy,
    NoAuth,
    QueryParameterAuth,
    StaticTokenAuth,
)
from bibliofabric.client import BaseApiClient
from bibliofabric.exceptions import AuthError

from .config import (
    BASE_MAX_CONCURRENCY,
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_MAX_REQUESTS_PER_SECOND,
    AlethecaSettings,
    AuthScheme,
    get_settings,
)
from .dialect import OPENALEX_API_BASE_URL
from .models import AutocompleteResult, RateLimitStatus
from .resources import (
    AuthorsClient,
    AwardsClient,
    FundersClient,
    InstitutionsClient,
    KeywordsClient,
    PublishersClient,
    SourcesClient,
    TopicsClient,
    WorksClient,
)
from .unwrapper import OpenAlexUnwrapper

logger = logging.getLogger(__name__)

_UNAUTHORIZED = 401
_TOO_MANY_REQUESTS = 429


class AlethecaClient(BaseApiClient):
    """Asynchronous client for the OpenAlex API.

    Credentials resolve in the constructor: an explicit ``api_key`` argument
    wins, then :class:`AlethecaSettings` (``ALETHECA_API_KEY`` or the
    consumer-legacy ``ALETHECA_OPENALEX_API_KEY`` env name). Without a key
    the client shares OpenAlex's $0.10/day per-IP budget and cannot use
    cursor paging past the first page; a free key fixes both.

    Usage::

        async with AlethecaClient(api_key="...") as client:
            work = await client.works.get("W1234567890")
    """

    def __init__(
        self,
        settings: AlethecaSettings | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        auth_strategy: AuthStrategy | None = None,
        auth_scheme: AuthScheme | None = None,
    ) -> None:
        """Build the client.

        Args:
            settings: Settings instance; ``None`` loads from the environment.
            api_key: OpenAlex API key; overrides the settings value.
            base_url: API base URL override (testing).
            auth_strategy: Fully custom auth strategy; takes precedence over
                ``api_key``/``auth_scheme``.
            auth_scheme: ``"query"`` (default, ``?api_key=``) or ``"bearer"``
                (``Authorization: Bearer``); overrides the settings value.
        """
        resolved_settings = settings or get_settings()
        if resolved_settings.max_requests_per_second is None:
            resolved_settings = resolved_settings.model_copy(
                update={"max_requests_per_second": DEFAULT_MAX_REQUESTS_PER_SECOND}
            )
        # The base default (10) is replaced by the stricter OpenAlex pace;
        # an explicit ALETHECA_MAX_CONCURRENCY of any other value is kept.
        if resolved_settings.max_concurrency == BASE_MAX_CONCURRENCY:
            resolved_settings = resolved_settings.model_copy(
                update={"max_concurrency": DEFAULT_MAX_CONCURRENCY}
            )
        key = api_key or resolved_settings.api_key
        scheme = auth_scheme or resolved_settings.auth_scheme
        if auth_strategy is not None:
            auth = auth_strategy
            keyless = isinstance(auth, NoAuth)
        else:
            auth = self._resolve_auth(key, scheme)
            keyless = key is None
        self._keyless = keyless
        super().__init__(
            base_url=base_url or OPENALEX_API_BASE_URL,
            settings=resolved_settings,
            unwrapper=OpenAlexUnwrapper(),
            auth=auth,
        )
        logger.debug("AlethecaClient initialized (keyless=%s).", keyless)

    @staticmethod
    def _resolve_auth(api_key: str | None, scheme: AuthScheme) -> AuthStrategy:
        """Pick the auth strategy for a key and scheme."""
        if not api_key:
            return NoAuth()
        if scheme == "bearer":
            return StaticTokenAuth(api_key)
        return QueryParameterAuth("api_key", api_key)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Send a request with retries, mapping keyless 401s to clear errors.

        OpenAlex 401s most often mean cursor paging without an API key; the
        re-raised message says how to fix it (OX-02).
        """
        try:
            return await super().request(
                method, path, params=params, json=json, headers=headers
            )
        except AuthError as error:
            response = error.response
            if (
                self._keyless
                and response is not None
                and response.status_code == _UNAUTHORIZED
            ):
                raise AuthError(
                    "OpenAlex rejected this request with 401. Keyless access "
                    "cannot use cursor paging past the first page and shares "
                    "a small daily budget per IP address. Get a free API key "
                    "at https://openalex.org/settings/api and set "
                    "ALETHECA_API_KEY (or pass api_key= to AlethecaClient).",
                    request=error.request,
                    response=response,
                ) from error
            raise

    def is_retryable(self, response: httpx.Response) -> bool:
        """Veto retries for 429s whose ``reason`` is ``daily_budget``.

        A daily-budget 429 will not succeed before the UTC midnight reset,
        so retrying only burns the caller's remaining budget (OX-15).
        """
        if response.status_code == _TOO_MANY_REQUESTS:
            try:
                body = response.json()
            except Exception:  # any body parse failure retries normally
                body = None
            if isinstance(body, dict) and body.get("reason") == "daily_budget":
                return False
        return super().is_retryable(response)

    # --- non-entity endpoints ------------------------------------------

    async def autocomplete(
        self, query: str, *, entity_type: str | None = None
    ) -> list[AutocompleteResult]:
        """Free typeahead/ID resolution; returns up to 10 rows per call.

        ``entity_type`` restricts to one entity route (e.g. ``"works"``,
        ``"authors"``, ``"institutions"``, ``"sources"``, ``"topics"``,
        ``"funders"``, ``"publishers"``, ``"awards"``, ``"keywords"``).
        Costs no credits.
        """
        path = "autocomplete" if entity_type is None else f"autocomplete/{entity_type}"
        body = await self.get_json(path, params={"q": query})
        return [
            AutocompleteResult.model_validate(row) for row in body.get("results") or []
        ]

    async def rate_limit(self) -> RateLimitStatus:
        """Return the key's remaining daily budget and per-second caps.

        Free, costs no credits; useful as a guard before large jobs.
        """
        return RateLimitStatus.model_validate(await self.get_json("rate-limit"))

    # --- entity resources -----------------------------------------------

    @cached_property
    def works(self) -> WorksClient:
        """The works resource client."""
        return WorksClient(self)

    @cached_property
    def authors(self) -> AuthorsClient:
        """The authors resource client."""
        return AuthorsClient(self)

    @cached_property
    def sources(self) -> SourcesClient:
        """The sources resource client."""
        return SourcesClient(self)

    @cached_property
    def institutions(self) -> InstitutionsClient:
        """The institutions resource client."""
        return InstitutionsClient(self)

    @cached_property
    def topics(self) -> TopicsClient:
        """The topics resource client."""
        return TopicsClient(self)

    @cached_property
    def keywords(self) -> KeywordsClient:
        """The keywords resource client."""
        return KeywordsClient(self)

    @cached_property
    def publishers(self) -> PublishersClient:
        """The publishers resource client."""
        return PublishersClient(self)

    @cached_property
    def funders(self) -> FundersClient:
        """The funders resource client."""
        return FundersClient(self)

    @cached_property
    def awards(self) -> AwardsClient:
        """The awards resource client."""
        return AwardsClient(self)
