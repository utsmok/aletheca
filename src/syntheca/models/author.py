"""Pydantic models for the Author entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import SummaryStats, TopicCount, TopicShare, YearCount
from .ids import AuthorIds
from .safe_types import SafeList, SafeStr


class Author(BaseEntity):
    """An OpenAlex Author entity."""

    ids: AuthorIds | None = None
    orcid: SafeStr | None = None
    display_name_alternatives: SafeList[str] = Field(default_factory=list)
    affiliations: SafeList[DehydratedInstitutionWithYear] = Field(
        default_factory=list
    )
    counts_by_year: SafeList[YearCount] = Field(default_factory=list)
    last_known_institutions: SafeList[DehydratedInstitution] = Field(
        default_factory=list
    )
    works_count: int | None = None
    cited_by_count: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None
    summary_stats: SummaryStats | None = None
    # Additional fields
    block_key: SafeStr | None = None
    full_name: SafeStr | None = None
    raw_author_names: SafeList[str] = Field(default_factory=list)

    # Deprecated: x_concepts → use topics
    x_concepts: SafeList[dict] = Field(default_factory=list)

    # Topics
    topics: SafeList[TopicCount] = Field(default_factory=list)
    topic_share: SafeList[TopicShare] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
