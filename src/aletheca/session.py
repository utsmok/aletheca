"""AlethecaSession — high-level async context manager for OpenAlex API access."""

from bibliofabric.log_config import configure_logging, logger

from . import queries
from .client import AlethecaClient
from .config import AlethecaSettings, get_settings

_DELEGATED_CLIENTS = frozenset(
    {
        "works",
        "authors",
        "sources",
        "institutions",
        "topics",
        "keywords",
        "publishers",
        "funders",
        "awards",
    }
)

configure_logging()


class _QueryAccessor:
    """Binds an AlethecaSession to convenience query functions."""

    def __init__(self, queries_module, session):
        self._module = queries_module
        self._session = session

    def __getattr__(self, name):
        attr = getattr(self._module, name)
        if callable(attr):
            from functools import partial

            return partial(attr, self._session)
        return attr


class AlethecaSession:
    """High-level session manager for interacting with the OpenAlex API.

    Usage::

        async with AlethecaSession() as session:
            works = await session.works.search(
                search="machine learning"
            )
            for work in works.results:
                print(work.title)

        # With API key
        async with AlethecaSession(api_key="...") as session:
            count = await session.works.count()
    """

    def __init__(
        self,
        settings: AlethecaSettings | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize the AlethecaSession.

        Args:
            settings: Optional AlethecaSettings. If None, loads from env.
            api_key: Optional OpenAlex API key (overrides settings).
            base_url: Optional API base URL override.
        """
        self._settings = settings or get_settings()
        self._api_client = AlethecaClient(
            settings=self._settings,
            api_key=api_key,
            base_url=base_url,
        )
        logger.debug("AlethecaSession initialized.")

    @property
    def queries(self):
        """Access convenience query functions."""
        return _QueryAccessor(queries, self)

    def __getattr__(self, name: str):
        if name in _DELEGATED_CLIENTS:
            return getattr(self._api_client, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __dir__(self):
        return list(super().__dir__()) + list(_DELEGATED_CLIENTS)

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self._api_client.aclose()

    async def __aenter__(self) -> "AlethecaSession":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
