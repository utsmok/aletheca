"""Pydantic models for the Source entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import APCEntry, Society, SummaryStats, TopicCount, TopicShare, YearCount
from .ids import SourceIds
from .safe_types import SafeList, SafeStr


class Source(BaseEntity):
    """An OpenAlex Source entity (journal, repository, conference, etc.)."""

    ids: SourceIds | None = None
    is_core: bool | None = None
    is_in_doaj: bool | None = None
    is_oa: bool | None = None
    type: str | None = None

    abbreviated_title: SafeStr | None = None
    alternate_titles: SafeList[str] = Field(default_factory=list)
    apc_prices: SafeList[APCEntry] = Field(default_factory=list)
    apc_usd: int | None = None
    country_code: SafeStr | None = None
    counts_by_year: SafeList[YearCount] = Field(default_factory=list)
    homepage_url: SafeStr | None = None
    host_organization: SafeStr | None = None
    host_organization_lineage: SafeList[str] = Field(default_factory=list)
    host_organization_name: SafeStr | None = None
    issn: SafeList[str] = Field(default_factory=list)
    issn_l: SafeStr | None = None
    societies: SafeList[Society] = Field(default_factory=list)
    works_count: int | None = None
    cited_by_count: int | None = None
    works_api_url: SafeStr | None = None

    # Deprecated
    x_concepts: SafeList[dict] = Field(default_factory=list)

    # Topics
    topics: SafeList[TopicCount] = Field(default_factory=list)
    topic_share: SafeList[TopicShare] = Field(default_factory=list)

    # Undocumented
    is_indexed_in_scopus: bool | None = None
    relevance_score: float | None = None
    oa_flip_year: int | None = None
    is_high_oa_rate: bool | None = None
    is_ojs: bool | None = None
    is_in_scielo: bool | None = None
    is_in_jstage: bool | None = None
    is_in_jstage_since_year: int | None = None
    is_high_oa_rate_since_year: int | None = None
    is_in_doaj_since_year: int | None = None
    oa_works_count: int | None = None
    last_publication_year: int | None = None
    first_publication_year: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    summary_stats: SummaryStats | None = None

    model_config = ConfigDict(extra="allow")
