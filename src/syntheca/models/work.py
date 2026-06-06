"""Pydantic models for the Work entity and its nested types."""

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import (
    SDG,
    APCData,
    Biblio,
    CitationNormalizedPercentile,
    DehydratedFunder,
    DehydratedKeyword,
    DehydratedTopic,
    Grant,
    HasContent,
    Location,
    Mesh,
    OpenAccess,
    YearCountBasic,
)
from .ids import WorkIds
from .safe_types import SafeList, SafeStr


class DehydratedSource(BaseEntity):
    """Minimal source info embedded in locations."""

    is_core: bool | None = None
    issn: SafeList[str] = Field(default_factory=list)
    issn_l: SafeStr | None = None
    type: str | None = None
    host_organization: SafeStr | None = None
    host_organization_name: SafeStr | None = None
    host_organization_lineage: SafeList[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class Authorship(BaseModel):
    """Authorship info on a work."""

    author_position: SafeStr | None = None
    author: dict | None = None
    institutions: SafeList[dict] = Field(default_factory=list)
    countries: SafeList[str] = Field(default_factory=list)
    is_corresponding: bool | None = None
    raw_affiliation_strings: SafeList[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class Work(BaseEntity):
    """An OpenAlex Work entity."""

    # Core fields
    title: SafeStr | None = None
    publication_year: int | None = None
    publication_date: SafeStr | None = None
    doi: SafeStr | None = None
    ids: WorkIds | None = None
    type: str | None = None
    open_access: OpenAccess | None = None

    # Bool flags
    has_fulltext: bool | None = None
    is_paratext: bool | None = None
    is_retracted: bool | None = None

    # Counts
    cited_by_count: int = 0
    locations_count: int = 0
    countries_distinct_count: int | None = None
    institutions_distinct_count: int | None = None
    works_count: int | None = None

    # Nested
    abstract_inverted_index: dict[str, list[int]] | None = None
    authorships: SafeList[Authorship] = Field(default_factory=list)
    apc_list: APCData | None = None
    apc_paid: APCData | None = None
    best_oa_location: Location | None = None
    biblio: Biblio | None = None
    citation_normalized_percentile: CitationNormalizedPercentile | None = None
    cited_by_api_url: SafeStr | None = None
    concepts: SafeList[dict] = Field(default_factory=list)
    corresponding_author_ids: SafeList[str] = Field(default_factory=list)
    corresponding_institution_ids: SafeList[str] = Field(default_factory=list)
    counts_by_year: SafeList[YearCountBasic] = Field(default_factory=list)
    fulltext_origin: str | None = None
    fwci: float | None = None
    grants: SafeList[Grant] = Field(default_factory=list)
    indexed_in: SafeList[str] = Field(default_factory=list)
    keywords: SafeList[DehydratedKeyword] = Field(default_factory=list)
    language: SafeStr | None = None
    license: SafeStr | None = None
    locations: SafeList[Location] = Field(default_factory=list)
    mesh: SafeList[Mesh] = Field(default_factory=list)
    primary_location: Location | None = None
    primary_topic: DehydratedTopic | None = None
    referenced_works: SafeList[str] = Field(default_factory=list)
    related_works: SafeList[str] = Field(default_factory=list)
    sustainable_development_goals: SafeList[SDG] = Field(default_factory=list)
    topics: SafeList[DehydratedTopic] = Field(default_factory=list)
    type_crossref: str | None = None
    has_content: HasContent | None = None
    cited_by_percentile_year: dict[str, int] | None = None
    datasets: list | None = None
    versions: SafeList[str] = Field(default_factory=list)
    referenced_works_count: int | None = None

    # Undocumented
    institution_assertions: SafeList[str] = Field(default_factory=list)
    funders: SafeList[DehydratedFunder] = Field(default_factory=list)
    institutions: SafeList[dict] = Field(default_factory=list)
    is_xpac: bool | None = None
    awards: SafeList[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")
