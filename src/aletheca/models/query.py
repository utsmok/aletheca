"""Typed shapes for OpenAlex endpoints that return neither entity nor page.

``GroupByBucket`` is the bucket of a ``group_by`` response,
``AutocompleteResult`` the row of ``/autocomplete``,
``RateLimitStatus`` the body of ``/rate-limit``, ``Link`` the edge of
``/links``, and ``LocationRecord`` the row of ``/locations``.
"""

from typing import Literal

from bibliofabric import SafeStr
from pydantic import BaseModel, ConfigDict, Field


class GroupByBucket(BaseModel):
    """One bucket of a ``group_by`` response.

    Multi-field ``group_by`` (up to three comma-separated fields) nests the
    second and third dimension in ``groups``.
    """

    key: str | int
    key_display_name: str | None = Field(None, alias="key_display_name")
    count: int
    groups: list["GroupByBucket"] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class AutocompleteResult(BaseModel):
    """One row of a free ``/autocomplete`` (or ``/autocomplete/{entity}``) response."""

    id: str | None = None
    short_id: str | None = None
    display_name: str | None = None
    hint: str | None = None
    cited_by_count: int | None = None
    works_count: int | None = None
    entity_type: str | None = None
    external_id: str | None = None
    filter_key: str | None = None

    model_config = ConfigDict(extra="ignore")


class PerSecondLimits(BaseModel):
    """The per-second request caps of one API key."""

    all_requests: int | None = None
    searches_with_more_than_5_boolean_operators: int | None = None
    filters_with_more_than_10_topic_or_concept_ids: int | None = None
    semantic_search: int | None = None

    model_config = ConfigDict(extra="ignore")


class RateLimitInfo(BaseModel):
    """Budget and rate state of one OpenAlex API key."""

    daily_budget_usd: float | None = None
    daily_used_usd: float | None = None
    daily_remaining_usd: float | None = None
    prepaid_balance_usd: float | None = None
    prepaid_remaining_usd: float | None = None
    prepaid_expires_at: str | None = None
    resets_at: str | None = None
    resets_in_seconds: int | None = None
    per_second_limits: PerSecondLimits | None = None
    credits_limit: int | None = None
    credits_used: int | None = None
    credits_remaining: int | None = None

    model_config = ConfigDict(extra="ignore")


class RateLimitStatus(BaseModel):
    """The body of ``GET /rate-limit`` (free, costs no credits).

    The echoed ``api_key`` field is ignored on purpose so the secret never
    lands in the model or its ``repr``.
    """

    is_grandfathered: bool | None = None
    rate_limit: RateLimitInfo | None = None

    model_config = ConfigDict(extra="ignore")


class LocationRecordId(BaseModel):
    """One native identifier attached to a location row."""

    id: str | None = None
    namespace: str | None = None
    relationship: str | None = None

    model_config = ConfigDict(extra="ignore")


class LocationRecordUrl(BaseModel):
    """One access URL attached to a location row."""

    url: str | None = None
    content_type: str | None = None

    model_config = ConfigDict(extra="ignore")


class LocationRecord(BaseModel):
    """One row of the ``/locations`` per-copy index.

    Each row is one copy of a work at one source, keyed by namespaced ids
    (``doi:...``, ``pmh:...``, ``pmid:...``, ``mag:...``). ``source_id``,
    ``source_name``, and ``publisher`` are flattened from the row's source.
    """

    id: SafeStr | None = None
    work_id: SafeStr | None = None
    native_id: SafeStr | None = None
    native_id_namespace: SafeStr | None = None
    provenance: SafeStr | None = None
    doi: SafeStr | None = None
    endpoint_id: SafeStr | None = None
    title: SafeStr | None = None
    type: SafeStr | None = None
    raw_type: SafeStr | None = None
    source_id: SafeStr | None = None
    source_name: SafeStr | None = None
    publisher: SafeStr | None = None
    is_oa: bool | None = None
    version: (
        Literal["publishedVersion", "acceptedVersion", "submittedVersion"] | None
    ) = None
    license: SafeStr | None = None
    language: SafeStr | None = None
    is_retracted: bool | None = None
    landing_page_url: SafeStr | None = None
    pdf_url: SafeStr | None = None
    ids: list[LocationRecordId] = Field(default_factory=list)
    urls: list[LocationRecordUrl] = Field(default_factory=list)
    merge_key: dict[str, str | None] | None = None
    ingested_at: str | None = None

    model_config = ConfigDict(extra="allow")


class Link(BaseModel):
    """One typed edge of the ``/links`` citation-graph endpoint.

    ``relationship`` is an OpenAlex relationship URL (for example
    ``https://openalex.org/relationships/citation``) labeling how
    ``origin`` relates to ``target``.
    """

    origin: SafeStr
    target: SafeStr
    relationship: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
