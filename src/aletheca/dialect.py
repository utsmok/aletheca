"""OpenAlex query dialect and the shared resource-client base.

``OPENALEX_DIALECT`` tells bibliofabric how OpenAlex names its query
parameters; :class:`OpenAlexResourceClient` adds the OpenAlex filter syntax,
batch-OR semantics, identifier normalization, and the cost-saving defaults
documented in the phase 2 research.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from bibliofabric.exceptions import ConfigurationError
from bibliofabric.ids import is_doi, normalize_doi
from bibliofabric.paging import QueryDialect
from bibliofabric.resources import ResourceClient
from pydantic import BaseModel

#: Base URL of the OpenAlex API.
OPENALEX_API_BASE_URL = "https://api.openalex.org"

#: OpenAlex caps pipe-joined OR lists at 100 values per filter.
MAX_OR_VALUES = 100

OPENALEX_DIALECT = QueryDialect(
    page_size_param="per-page",
    max_page_size=100,
    default_page_size=25,
    page_param="page",
    page_start=1,
    cursor_param="cursor",
    cursor_start="*",
    sort_param="sort",
    query_param="search",
    select_param="select",
)

_OPENALEX_URL_PREFIX = "https://openalex.org/"

#: Filter fields whose values are DOIs and need prefix/case normalization
#: before they may join a ``filter=`` value (raw URL forms inject colons).
DOI_FIELDS = frozenset({"doi"})


def _normalize_filter_value(field: str, value: Any) -> str:
    """Stringify one filter value the way OpenAlex expects.

    Booleans serialize lowercase (``is_oa:true``); lists/tuples join with
    ``|`` (OR), DOIs inside OR lists are normalized first. Values that carry
    spaces or commas need quoting by the caller (OpenAlex rule).
    """
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list | tuple):
        values = [str(item) for item in value]
        if field in DOI_FIELDS:
            values = [normalize_doi(item) for item in values]
        if len(values) > MAX_OR_VALUES:
            raise ConfigurationError(
                f"OpenAlex allows at most {MAX_OR_VALUES} pipe-separated "
                f"values per filter; got {len(values)} for '{field}'."
            )
        return "|".join(values)
    if field in DOI_FIELDS:
        return normalize_doi(str(value))
    return str(value)


class OpenAlexResourceClient[E: BaseModel](ResourceClient[E]):
    """Base for all OpenAlex resource clients.

    Encodes the OpenAlex API shape on top of bibliofabric's generic
    :class:`bibliofabric.resources.ResourceClient`: the single ``filter=``
    parameter, pipe-joined OR batches of up to 100 ids, DOI/ORCID/ROR
    normalization, cursor iteration at ``per-page=100``, and a minimal-cost
    ``count()``.
    """

    dialect = OPENALEX_DIALECT
    batch_size = MAX_OR_VALUES

    # --- hooks ---------------------------------------------------------

    def normalize_id(self, value: str) -> str:
        """Canonicalize an identifier used in paths, batches, and dict keys.

        Strips ``https://openalex.org/`` and the entity path prefix, and
        lowercases values that look like DOIs so caller inputs and returned
        record keys always match (DOIs are case-insensitive).
        """
        text = value.strip()
        text = text.removeprefix(_OPENALEX_URL_PREFIX)
        text = text.removeprefix(f"{self.path}/")
        if is_doi(text):
            return normalize_doi(text)
        return text

    def build_filter_params(
        self, filters: BaseModel | Mapping[str, Any] | None
    ) -> dict[str, str]:
        """Serialize filters into OpenAlex's single ``filter`` parameter.

        ``filter=publication_year:2024,is_oa:true``; list values become
        pipe-joined OR groups (max :data:`MAX_OR_VALUES`).
        """
        if filters is None:
            return {}
        if isinstance(filters, BaseModel):
            dumped = filters.model_dump(exclude_none=True, by_alias=True)
        else:
            dumped = dict(filters)
        if not dumped:
            return {}
        parts = [
            f"{key}:{_normalize_filter_value(key, value)}"
            for key, value in dumped.items()
        ]
        return {"filter": ",".join(parts)}

    def build_batch_params(self, field: str, values: Sequence[str]) -> dict[str, str]:
        """Build one ``batch_get`` chunk as a pipe-joined OR filter.

        DOI fields are normalized first (AT-03): URL forms would inject
        colons into the ``filter=`` value. The default ``field="id"`` maps to
        the ``openalex`` filter, because OpenAlex has no ``id`` filter.
        """
        chunk = list(values)
        if field in DOI_FIELDS:
            chunk = [normalize_doi(value) for value in chunk]
        filter_key = "openalex" if field == "id" else field
        return {"filter": f"{filter_key}:{'|'.join(chunk)}"}

    # --- operations ----------------------------------------------------

    def iterate(self, filters=None, **kwargs: Any) -> Any:  # noqa: ANN401
        """Iterate over all matching entities via cursor paging.

        Defaults to ``per-page=100`` (search keeps the documented default of
        25). Keyless access can only fetch the first cursor page; the client
        turns the follow-up 401 into an actionable :class:`AuthError`.
        """
        if kwargs.get("page_size") is None:
            kwargs["page_size"] = self.dialect.max_page_size
        return super().iterate(filters, **kwargs)

    async def count(
        self,
        filters: BaseModel | Mapping[str, Any] | None = None,
        *,
        query: str | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> int:
        """Return the total number of matching entities at minimal cost.

        Sends ``per-page=1`` (the core default) plus ``select=id`` so the
        one-credit count request carries no entity payloads.
        """
        merged = {"select": "id", **(params or {})}
        return await super().count(filters, query=query, params=merged)
