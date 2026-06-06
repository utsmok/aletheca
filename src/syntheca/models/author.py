"""Pydantic models for the Author entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import TopicCount, TopicShare, YearCount
from .dehydrated import DehydratedInstitution, DehydratedInstitutionWithYear
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

    # Deprecated: x_concepts → use topics
    x_concepts: SafeList[dict] = Field(default_factory=list)

    # Topics
    topics: SafeList[TopicCount] = Field(default_factory=list)
    topic_share: SafeList[TopicShare] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
