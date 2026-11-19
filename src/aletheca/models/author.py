"""Pydantic models for the Author entity."""

from bibliofabric import SafeList, SafeStr
from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import SummaryStats, TopicCount, TopicShare, YearCount
from .dehydrated import (
    DehydratedConcept,
    DehydratedInstitution,
    DehydratedInstitutionWithYear,
)
from .ids import AuthorIds


class Author(BaseEntity):
    """An OpenAlex Author entity."""

    ids: AuthorIds | None = None
    orcid: SafeStr | None = None
    display_name_alternatives: SafeList[str] = Field(default_factory=list)
    affiliations: SafeList[DehydratedInstitutionWithYear] = Field(default_factory=list)
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
    awards_api_url: SafeStr | None = None
    awards_count: int | None = None
    observed_orcids: SafeList[str] = Field(default_factory=list)
    summary_stats: SummaryStats | None = None
    # Additional fields
    block_key: SafeStr | None = None
    full_name: SafeStr | None = None
    raw_author_names: SafeList[str] = Field(default_factory=list)

    # Deprecated: x_concepts → use topics
    x_concepts: SafeList[DehydratedConcept] = Field(
        default_factory=list,
        description="Deprecated upstream: replaced by topics, but still returned.",
    )

    # Topics
    topics: SafeList[TopicCount] = Field(default_factory=list)
    topic_share: SafeList[TopicShare] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
