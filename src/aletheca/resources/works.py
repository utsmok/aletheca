"""Client for the OpenAlex works endpoint."""

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from bibliofabric.exceptions import ConfigurationError
from bibliofabric.paging import Page
from pydantic import BaseModel

from ..dialect import OpenAlexResourceClient
from ..models import GroupByBucket, Work

VALID_CORPUS_VALUES = ("core", "expansion", "all")
MAX_SAMPLE_SIZE = 10_000
SEARCH_SCOPES = (
    "title",
    "title_and_abstract",
    "title_abstract_keywords",
    "exact",
    "semantic",
)


class WorksClient(OpenAlexResourceClient[Work]):
    """Client for the ``/works`` endpoint.

    Adds the works-only query features: ``corpus``/``include_pulled``/
    ``include_parts``, ``sample``/``seed``, ``group_by``, the scoped
    ``search.*`` parameters, and DOI-based batch retrieval.
    """

    path = "works"
    model = Work

    async def search(
        self,
        filters: BaseModel | Mapping[str, Any] | None = None,
        *,
        query: str | None = None,
        sort: str | Sequence[str] | None = None,
        select: Sequence[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        cursor: str | None = None,
        params: Mapping[str, Any] | None = None,
        corpus: Literal["core", "expansion", "all"] | None = None,
        include_parts: bool | None = None,
        include_pulled: bool | None = None,
    ) -> Page[Work]:
        """Search works; accepts the works-only corpus controls.

        ``corpus`` selects which works answer: ``core`` (default upstream)
        excludes pulled and part works, ``expansion`` is the expansion set,
        ``all`` is everything. ``include_parts``/``include_pulled`` re-add
        those subsets to ``core``. Note that a ``is_pulled``/``is_retracted``
        filter re-includes pulled works on its own.
        """
        extra = dict(params or {})
        if corpus is not None:
            if corpus not in VALID_CORPUS_VALUES:
                raise ConfigurationError(
                    f"corpus must be one of {VALID_CORPUS_VALUES}, got {corpus!r}."
                )
            extra["corpus"] = corpus
        if include_parts is not None:
            extra["include_parts"] = str(include_parts).lower()
        if include_pulled is not None:
            extra["include_pulled"] = str(include_pulled).lower()
        return await super().search(
            filters,
            query=query,
            sort=sort,
            select=select,
            page=page,
            page_size=page_size,
            cursor=cursor,
            params=extra or None,
        )

    async def search_scoped(
        self,
        text: str,
        *,
        scope: Literal[
            "title",
            "title_and_abstract",
            "title_abstract_keywords",
            "exact",
            "semantic",
        ] = "title_and_abstract",
        filters: BaseModel | Mapping[str, Any] | None = None,
        sort: str | Sequence[str] | None = None,
        select: Sequence[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Work]:
        """Search works under one scoped ``search.*`` parameter.

        Scopes: ``title``, ``title_and_abstract``, ``title_abstract_keywords``,
        ``exact`` (supports wildcards and proximity operators), and
        ``semantic`` (embedding search; max 50 results, 1 request/second, and
        only its whitelisted filters combine). Only one search parameter is
        allowed per request; a search costs 10 credits.
        """
        if scope not in SEARCH_SCOPES:
            raise ConfigurationError(
                f"scope must be one of {SEARCH_SCOPES}, got {scope!r}."
            )
        return await self.search(
            filters,
            sort=sort,
            select=select,
            page=page,
            page_size=page_size,
            params={f"search.{scope}": text},
        )

    async def sample(
        self,
        n: int,
        *,
        seed: int | None = None,
        filters: BaseModel | Mapping[str, Any] | None = None,
        query: str | None = None,
        sort: str | Sequence[str] | None = None,
        select: Sequence[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Page[Work]:
        """Return a random sample of up to ``n`` works (max 10,000).

        Pass ``seed`` for reproducibility. ``Page.total`` reports the sample
        size, not the size of the filtered corpus.
        """
        if not 0 < n <= MAX_SAMPLE_SIZE:
            raise ConfigurationError(
                f"sample size must be between 1 and {MAX_SAMPLE_SIZE}, got {n}."
            )
        extra: dict[str, Any] = {"sample": n}
        if seed is not None:
            extra["seed"] = seed
        return await self.search(
            filters,
            query=query,
            sort=sort,
            select=select,
            page=page,
            page_size=page_size,
            params=extra,
        )

    async def group_by(
        self,
        group_by: str,
        *,
        filters: BaseModel | Mapping[str, Any] | None = None,
        query: str | None = None,
        cursor: str | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> list[GroupByBucket]:
        """Return typed ``group_by`` buckets (costs one credit).

        ``group_by`` accepts up to three comma-separated fields; deeper
        dimensions nest in :attr:`GroupByBucket.groups`. Responses page at 200
        buckets with a cursor; pass ``cursor=<next cursor from Page.meta>`` to
        continue. Pass ``cursor="*"`` to start cursor paging explicitly.
        """
        extra = dict(params or {})
        extra["group_by"] = group_by
        if cursor is not None:
            extra["cursor"] = cursor
        query_params = self.build_filter_params(filters)
        if query is not None and self.dialect.query_param is not None:
            query_params[self.dialect.query_param] = query
        query_params.update(extra)
        response = await self._client.request("GET", self.path, params=query_params)
        body = response.json()
        return [
            GroupByBucket.model_validate(bucket)
            for bucket in body.get("group_by") or []
        ]

    async def batch_get_by_doi(
        self, dois: Sequence[str], *, batch_size: int | None = None
    ) -> dict[str, Work]:
        """Fetch works by DOI, batched as pipe-joined OR filters.

        DOIs are normalized (URL prefixes stripped, lowercased) and split
        into chunks of ``batch_size`` (default 100, the OpenAlex OR cap).
        Returns ``{normalized doi: Work}``; DOIs not found are absent. Works
        without a DOI fall back to their OpenAlex id as key.
        """
        return await self.batch_get(dois, field="doi", batch_size=batch_size)

    async def batch_get_by_openalex_id(
        self, ids: Sequence[str], *, batch_size: int | None = None
    ) -> dict[str, Work]:
        """Fetch works by OpenAlex id (bare ``W...`` or full URL)."""
        return await self.batch_get(ids, field="openalex", batch_size=batch_size)

    async def citing(
        self,
        work_id: str,
        *,
        limit: int = 100,
        filters: BaseModel | Mapping[str, Any] | None = None,
        sort: str | Sequence[str] | None = None,
    ) -> list[Work]:
        """Collect works that cite ``work_id``, bounded by ``limit``."""
        merged: dict[str, Any] = {"cites": self.normalize_id(work_id)}
        if filters is not None:
            extra = (
                filters.model_dump(exclude_none=True, by_alias=True)
                if isinstance(filters, BaseModel)
                else dict(filters)
            )
            merged.update(extra)
        return await self.collect(merged, sort=sort, limit=limit)

    async def referenced(self, work_id: str, *, limit: int = 100) -> list[Work]:
        """Fetch (up to ``limit`` of) the works referenced by ``work_id``."""
        work = await self.get(work_id)
        targets = [self.normalize_id(target) for target in work.referenced_works]
        targets = targets[:limit]
        if not targets:
            return []
        results = await self.batch_get(targets, field="openalex")
        return [results[target] for target in targets if target in results]
