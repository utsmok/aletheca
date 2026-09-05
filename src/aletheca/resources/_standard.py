"""AlethecaResourceClient — base class for all OpenAlex resource clients.

Overrides bibliofabric's parameter names and filter serialization
for OpenAlex-specific conventions:

- ``per_page`` instead of ``pageSize``
- ``sort`` instead of ``sortBy``
- ``filter=key:value,key:value`` instead of individual query params

Subclasses that declare ``_batch_fields`` (a dict mapping a friendly name
to an OpenAlex filter field) automatically get ``batch_get_by_<name>()``
convenience methods at class-creation time.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bibliofabric.exceptions import BibliofabricError
from bibliofabric.log_config import logger
from bibliofabric.resources import (
    BaseResourceClient,
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)
from pydantic import BaseModel

#: Maximum identifiers per pipe-separated filter (OpenAlex limit).
BATCH_GET_SIZE = 50

# ── ID normalization prefixes ──────────────────────────────────────────────

_URL_PREFIXES: dict[str, tuple[str, ...]] = {
    "doi": ("https://doi.org/", "http://doi.org/"),
    "openalex": ("https://openalex.org/",),
    "orcid": ("https://orcid.org/", "http://orcid.org/"),
    "ror": ("https://ror.org/",),
    "pmid": (),
    "pmcid": (),
    "issn": (),
    "mag": (),
}


def _normalize_id(raw: str, field: str) -> str:
    """Lowercase and strip known URL prefixes for a given filter field."""
    key = str(raw).lower().strip()
    for prefix in _URL_PREFIXES.get(field, ()):
        key = key.replace(prefix, "")
    return key


_OPENALEX_ID_PREFIX = "https://openalex.org/"


# ── Auto-generated batch method factory ────────────────────────────────────


def _make_batch_getter(field: str) -> Any:
    """Return an async method that delegates to :meth:`batch_get`."""

    async def _batch_get_by(
        self: AlethecaResourceClient,
        identifiers: list[str],
        *,
        batch_size: int = BATCH_GET_SIZE,
    ) -> dict[str, Any]:
        return await self.batch_get(identifiers, field=field, batch_size=batch_size)

    return _batch_get_by


# ── Base classes ───────────────────────────────────────────────────────────


class AlethecaResourceClient(BaseResourceClient):
    """Base for all OpenAlex resource clients.

    Sets OpenAlex-specific parameter names and overrides filter
    serialization to produce the ``filter=key:value,key:value``
    query string format.

    Subclasses may declare ``_batch_fields`` to auto-generate
    ``batch_get_by_<name>()`` convenience methods.
    """

    _param_page_size: str | None = "per_page"
    _param_sort: str | None = "sort"
    #: API route for the entity; set by concrete subclasses (e.g. ``"works"``).
    _entity_path: str
    _entity_model: type[BaseModel] | None = None
    _search_response_model: type[BaseModel] | None = None

    #: Override in subclasses.  Maps ``method_suffix`` → ``filter_field``.
    #: For example ``{"doi": "doi", "openalex_id": "openalex"}`` produces
    #: ``batch_get_by_doi()`` and ``batch_get_by_openalex_id()``.
    _batch_fields: dict[str, str] = {}

    async def get(self, entity_id: str) -> Any:
        """Retrieve one entity by ID (bare ID or full ``openalex.org`` URL).

        Entity records carry full-URL ids (``https://openalex.org/W123`` or
        slug-keyed ``https://openalex.org/keywords/photosynthesis``), but the
        single-entity route only accepts the key after the entity path.
        DOI/ORCID/ROR URLs are passed through untouched.
        """
        return await GettableMixin.get(self, self._normalize_entity_id(entity_id))

    def _normalize_entity_id(self, raw: str) -> str:
        """Reduce an entity URL to its route key."""
        key = str(raw).strip().removeprefix(_OPENALEX_ID_PREFIX)
        return key.removeprefix(f"{self._entity_path}/")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for suffix, field in getattr(cls, "_batch_fields", {}).items():
            method_name = f"batch_get_by_{suffix}"
            # Only attach if not already defined (allows manual overrides)
            if not hasattr(cls, method_name):
                setattr(cls, method_name, _make_batch_getter(field))

    def _serialize_filters(
        self, filters: BaseModel | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Serialize filters into OpenAlex's single ``filter`` query parameter.

        OpenAlex syntax::

            filter=publication_year:2024,is_oa:true
            filter=authorships.author.id:A123|A456

        Returns a dict with a single ``filter`` key containing the
        comma-joined filter string.
        """
        if filters is None:
            return {}
        if isinstance(filters, BaseModel):
            filter_dict = filters.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(filters, dict):
            filter_dict = dict(filters)
        else:
            raise BibliofabricError(
                f"filters must be a Pydantic model or dictionary, got {type(filters)}"
            )
        if not filter_dict:
            return {}
        parts = []
        for key, value in filter_dict.items():
            parts.append(f"{key}:{value}")
        return {"filter": ",".join(parts)}

    async def count(
        self,
        *,
        filters: BaseModel | dict[str, Any] | None = None,
        search: str | None = None,
    ) -> int:
        """Return total number of matching entities.

        Performs a minimal search (page_size=1) and reads ``meta.count``
        from the OpenAlex response envelope.
        """
        response = await self.search(  # ty: ignore[unresolved-attribute]
            page=1, page_size=1, filters=filters, search=search
        )
        if isinstance(response, BaseModel) and hasattr(response, "meta"):
            meta = response.meta
            if hasattr(meta, "count") and meta.count is not None:
                return int(meta.count)
        return 0

    async def batch_get(
        self,
        identifiers: list[str],
        *,
        field: str = "doi",
        key_fn: Callable[[Any], str] | None = None,
        batch_size: int = BATCH_GET_SIZE,
    ) -> dict[str, Any]:
        """Retrieve multiple entities by identifier in batched pipe-separated queries.

        Automatically splits *identifiers* into groups of *batch_size* (default 50,
        the OpenAlex maximum) and issues one ``search`` per group using the
        pipe-separated OR syntax::

            filter=doi:10.1234/a|10.5678/b|...

        Results are returned as ``{identifier: entity}``; identifiers not found
        in OpenAlex are omitted from the dict.

        For common identifier types use the auto-generated convenience methods
        (e.g. ``batch_get_by_doi``, ``batch_get_by_openalex_id``) instead.

        Args:
            identifiers: Values to look up (DOIs, OpenAlex IDs, etc.).
            field: Filter field name (e.g. ``"doi"``, ``"openalex"``).
            key_fn: Optional function to extract the lookup key from a
                parsed entity.  Defaults to extracting and normalising
                ``entity.<field>``.
            batch_size: Max identifiers per API call (1–50).

        Returns:
            Dict mapping each *identifier* to its parsed entity (Pydantic model).
            Identifiers not found are absent from the dict.
        """
        if not identifiers:
            return {}
        batch_size = max(1, min(batch_size, BATCH_GET_SIZE))
        results: dict[str, Any] = {}
        for i in range(0, len(identifiers), batch_size):
            batch = identifiers[i : i + batch_size]
            pipe_value = "|".join(batch)
            response = await self.search(  # ty: ignore[unresolved-attribute]
                page=1,
                page_size=batch_size,
                filters={field: pipe_value},
            )
            entities = self._extract_results(response)
            for entity in entities:
                key = self._resolve_key(entity, field, key_fn)
                if key is not None:
                    results[key] = entity
        return results

    @staticmethod
    def _extract_results(response: Any) -> list[Any]:
        """Pull the results list from a search response (model or raw dict)."""
        if isinstance(response, BaseModel) and hasattr(response, "results"):
            return list(response.results or [])
        if isinstance(response, dict):
            return list(response.get("results") or [])
        return []

    @staticmethod
    def _resolve_key(
        entity: Any,
        field: str,
        key_fn: Callable[[Any], str] | None,
    ) -> str | None:
        """Derive the lookup key from a parsed entity."""
        if key_fn is not None:
            return key_fn(entity)
        # For 'openalex' field, extract from the entity's 'id' attribute
        if field == "openalex":
            raw = getattr(entity, "id", None) if isinstance(entity, BaseModel) else None
            if raw is None and isinstance(entity, dict):
                raw = entity.get("id")
        else:
            raw = (
                getattr(entity, field, None) if isinstance(entity, BaseModel) else None
            )
            if raw is None and isinstance(entity, dict):
                raw = entity.get(field)
        if raw is None:
            return None
        # Handle list-valued fields (e.g. issn) — use first element
        if isinstance(raw, list):
            raw = raw[0] if raw else None
            if raw is None:
                return None
        return _normalize_id(raw, field)


class StandardResourceClient(
    SearchableMixin, CursorIterableMixin, AlethecaResourceClient
):
    """Base for standard CRUD resource clients that only differ in class attributes.

    Subclasses must set:

        _entity_path (str): The API path for the resource.
        _entity_model: Pydantic model for a single entity.
        _search_response_model: Pydantic model for the search response envelope.
    """

    _entity_path: str

    def __init__(self, api_client):  # noqa: ANN001
        super().__init__(api_client)
        logger.debug(f"{type(self).__name__} initialized for path: {self._entity_path}")
