"""
aletheca.entities

dataclasses to represent data retrieved from OpenAlex

based on the official docs: https://docs.openalex.org/api-entities/

"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Literal, TypedDict

# ----------------------------------------------------------------------------------------------------------------
# Type aliases
# ----------------------------------------------------------------------------------------------------------------

WorkType = Literal[
    "article",
    "book-chapter",
    "book-section",
    "book",
    "dataset",
    "database",
    "dissertation",
    "editorial",
    "erratum",
    "grant",
    "letter",
    "libguides",
    "other",
    "paratext",
    "peer-review",
    "preprint",
    "reference-entry",
    "report",
    "report-component",
    "retraction",
    "review",
    "software",
    "standard",
    "supplementary-materials",
]

WorkTypeCrossref = Literal[
    "book-section",
    "monograph",
    "report-component",
    "report",
    "peer-review",
    "book-track",
    "journal-article",
    "book-part",
    "other",
    "book",
    "journal-volume",
    "book-set",
    "reference-entry",
    "proceedings-article",
    "journal",
    "component",
    "book-chapter",
    "proceedings-series",
    "report-series",
    "proceedings",
    "database",
    "standard",
    "reference-book",
    "posted-content",
    "journal-issue",
    "dissertation",
    "grant",
    "dataset",
    "book-series",
    "edited-book",
]

SourceType = Literal[
    "journal",
    "repository",
    "conference",
    "ebook platform",
    "book series",
    "metadata",
    "other",
]

InstitutionType = Literal[
    "education",
    "healthcare",
    "company",
    "archive",
    "nonprofit",
    "government",
    "facility",
    "other",
]

# ----------------------------------------------------------------------------------------------------------------
# Base class(es)
# ----------------------------------------------------------------------------------------------------------------


@dataclass
class BaseOpenAlex:
    """
    Base class for OpenAlex entities with an id.
    All entity classes should inherit from this.
    """

    id: str  # openalex id
    display_name: str


# ----------------------------------------------------------------------------------------------------------------
#  Nested fields
# ----------------------------------------------------------------------------------------------------------------


@dataclass
class WorkIds:
    openalex: str
    doi: str | None = None
    mag: int | None = None
    pmid: str | None = None
    pmcid: str | None = None


@dataclass
class AuthorIds:
    openalex: str
    orcid: str | None = None
    scopus: str | None = None
    twitter: str | None = None
    wikipedia: str | None = None


@dataclass
class SourceIds:
    openalex: str
    fatcat: str | None = None
    issn: list[str | None] = field(default_factory=list)
    issn_l: str | None = None
    mag: int | None = None
    wikidata: str | None = None


@dataclass
class InstitutionIds:
    openalex: str
    ror: str | None = None
    grid: str | None = None
    mag: int | None = None
    wikidata: str | None = None
    wikipedia: str | None = None


@dataclass
class TopicIds:
    openalex: str
    wikidata: str | None = None


@dataclass
class PublisherIds:
    openalex: str
    ror: str | None = None
    wikidata: str | None = None


@dataclass
class FunderIds:
    openalex: str
    doi: str | None = None
    crossref: str | None = None
    ror: str | None = None
    wikidata: str | None = None


@dataclass
class ConceptIds:
    openalex: str
    mag: int | None = None
    umls_cui: list[str] | None = None
    umls_aui: list[str] | None = None
    wikidata: str | None = None
    wikipedia: str | None = None


@dataclass
class Affiliation:
    raw_affiliation_string: str
    institution_ids: list[str | None] = field(default_factory=list)


@dataclass
class DehydratedAuthor(BaseOpenAlex):
    orcid: str | None = None


@dataclass
class DehydratedInstitution(BaseOpenAlex):
    country_code: str | None = None  # ISO 3166-1 alpha-2 country code
    lineage: list[str | None] = field(default_factory=list)
    ror: str | None = None
    type: InstitutionType | None = None


@dataclass
class RelatedInstitution(DehydratedInstitution):
    relationship: Literal["parent", "child", "related"] | None = None


@dataclass
class DehydratedInstitutionWithYear(DehydratedInstitution):
    years: list[int | None] = field(default_factory=list)


@dataclass
class DehydratedSource(BaseOpenAlex):
    is_core: bool
    is_in_doaj: bool
    is_oa: bool
    type: SourceType
    issn_l: str | None = None
    issn: list[str] | None = None
    host_organization: str | None = None
    host_organization_lineage: list[str | None] = field(default_factory=list)
    host_organization_name: str | None = None


@dataclass
class Repository(BaseOpenAlex):
    # specific field for the 'repositories' field of Institution entity
    host_organization: str | None = None
    host_organization_lineage: list[str | None] = field(default_factory=list)
    host_organization_name: str | None = None


@dataclass
class DehydratedConcept(BaseOpenAlex):
    score: float
    level: int  # min 0 max 5
    wikidata: str


@dataclass
class Authorship:
    author: DehydratedAuthor
    raw_author_name: str
    is_corresponding: bool
    countries: list[str] = field(default_factory=list)
    author_position: Literal["first", "middle", "last"] | None = None
    affiliations: list[Affiliation] = field(default_factory=list)
    institutions: list[DehydratedInstitution] = field(default_factory=list)
    raw_affiliation_strings: list[str] = field(default_factory=list)


@dataclass
class APCData:
    value: int
    currency: str
    value_usd: int
    provenance: str | None = None


@dataclass
class APCEntry:
    price: int
    currency: str


@dataclass
class Biblio:
    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None


@dataclass
class Mesh:
    descriptor_ui: str
    descriptor_name: str
    qualifier_ui: str
    qualifier_name: str
    is_major_topic: bool


@dataclass
class Location:
    is_accepted: bool
    is_oa: bool
    is_published: bool
    landing_page_url: str | None = None
    pdf_url: str | None = None
    license: str | None = None
    source: DehydratedSource | None = None
    version: (
        Literal["publishedVersion", "acceptedVersion", "submittedVersion"] | None
    ) = None


@dataclass
class OpenAccess:
    is_oa: bool
    oa_status: Literal["diamond", "gold", "green", "hybrid", "bronze", "closed"]
    oa_url: str | None
    any_repository_has_fulltext: bool


@dataclass
class Grant:
    funder: str | None = None
    funder_display_name: str | None = None
    award_id: str | None = None


@dataclass
class Domain(BaseOpenAlex): ...


@dataclass
class Field(BaseOpenAlex): ...


@dataclass
class Subfield(BaseOpenAlex): ...


@dataclass
class TopicMinimal(BaseOpenAlex): ...


@dataclass
class DehydratedTopic(BaseOpenAlex):
    score: float
    subfield: Subfield
    field: Field
    domain: Domain


@dataclass
class TopicCount(BaseOpenAlex):
    count: int
    subfield: Subfield
    field: Field
    domain: Domain


@dataclass
class TopicShare(BaseOpenAlex):
    value: float
    subfield: Subfield
    field: Field
    domain: Domain


@dataclass
class SDG(BaseOpenAlex):
    score: float


@dataclass
class DehydratedKeyword(BaseOpenAlex):
    display_name: str
    score: float


class CitationNormalizedPercentile(TypedDict):
    value: float
    is_in_top_1_percent: bool
    is_in_top_10_percent: bool


class YearCountBasic(TypedDict):
    year: int
    cited_by_count: int


class YearCount(TypedDict):
    year: int
    cited_by_count: int
    works_count: int


class SummaryStats(TypedDict):
    two_yr_mean_citedness: float  # note: fieldname in OpenAlex is "2yr_mean_citedness" but cannot use that in Python!
    h_index: int
    i10_index: int


@dataclass
class Society:
    url: str | None = None
    organization: str | None = None


@dataclass
class Geo:
    city: str | None = None
    geonames_city_id: str | None = None
    region: str | None = None
    country_code: str | None = None  # ISO 3166-1 alpha-2 country code
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class Role(TypedDict):
    role: Literal["funder", "publisher", "institution"]
    id: str
    works_count: int


# ----------------------------------------------------------------------------------------------------------------
# Main entities
# ----------------------------------------------------------------------------------------------------------------


@dataclass
class Keyword(BaseOpenAlex):
    cited_by_count: int
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    works_count: int


@dataclass
class Topic(BaseOpenAlex):
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    works_count: int
    description: str
    ids: TopicIds
    keywords: list[str]
    subfield: Subfield
    field: Field
    domain: Domain
    cited_by_count: int
    works_api_url: str
    siblings: list[TopicMinimal] = dataclasses.field(default_factory=list)


@dataclass
class Author(BaseOpenAlex):
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string

    cited_by_count: int
    works_count: int

    ids: AuthorIds
    orcid: str | None

    summary_stats: dict[
        str, float | int
    ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness

    affiliations: list[DehydratedInstitutionWithYear | None] = field(
        default_factory=list
    )
    counts_by_year: list[YearCount | None] = field(default_factory=list)
    display_name_alternatives: list[str | None] = field(default_factory=list)
    last_known_institutions: list[DehydratedInstitution | None] = field(
        default_factory=list
    )
    works_api_url: str | None = None
    x_concepts: list[DehydratedConcept | None] = field(default_factory=list)

    # UNDOCUMENTED FIELDS
    topics: list[TopicCount | None] = field(default_factory=list)
    topic_share: list[TopicShare | None] = field(default_factory=list)


@dataclass
class Source(BaseOpenAlex):
    cited_by_count: int
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    ids: SourceIds
    is_core: bool
    is_in_doaj: bool
    is_oa: bool
    summary_stats: dict[
        str, float | int
    ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
    works_api_url: str
    works_count: int
    type: SourceType

    abbreviated_title: str | None = None
    alternate_titles: list[str | None] = field(default_factory=list)
    apc_prices: list[APCEntry | None] = field(default_factory=list)
    apc_usd: int | None = None
    country_code: str | None = None  # ISO 3166-1 alpha-2 country code
    counts_by_year: list[YearCount | None] = field(default_factory=list)
    homepage_url: str | None = None
    host_organization: str | None = None
    host_organization_lineage: list[str | None] = field(default_factory=list)
    host_organization_name: str | None = None
    issn: list[str | None] = field(default_factory=list)
    issn_l: str | None = None
    societies: list[Society | None] = field(default_factory=list)
    x_concepts: list[DehydratedConcept | None] = field(default_factory=list)

    # UNDOCUMENTED FIELDS
    is_indexed_in_scopus: bool = False
    topics: list[TopicCount | None] = field(default_factory=list)
    topic_share: list[TopicShare | None] = field(default_factory=list)


@dataclass
class Institution(BaseOpenAlex):
    cited_by_count: int
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    ids: InstitutionIds
    is_super_system: bool
    summary_stats: dict[
        str, float | int
    ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
    type: InstitutionType
    works_api_url: str
    works_count: int

    associated_institutions: list[RelatedInstitution | None] = field(
        default_factory=list
    )
    country_code: str | None = None  # ISO 3166-1 alpha-2 country code
    counts_by_year: list[YearCount | None] = field(default_factory=list)
    display_name_acronyms: list[str | None] = field(default_factory=list)
    display_name_alternatives: list[str | None] = field(default_factory=list)
    geo: Geo | None = None
    homepage_url: str | None = None
    image_thumbnail_url: str | None = None
    image_url: str | None = None
    international: dict[Literal["display_name"], dict[str, str] | None] = field(
        default_factory=dict
    )
    lineage: list[str | None] = field(default_factory=list)
    repositories: list[Repository | None] = field(default_factory=list)
    roles: list[Role | None] = field(default_factory=list)
    ror: str | None = None
    x_concepts: list[DehydratedConcept | None] = field(default_factory=list)

    # UNDOCUMENTED FIELDS
    type_id: str | None = None
    topics: list[TopicCount | None] = field(default_factory=list)
    topic_share: list[TopicShare | None] = field(default_factory=list)


@dataclass
class Publisher(BaseOpenAlex):
    cited_by_count: int
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    hierarchy_level: int
    ids: PublisherIds
    sources_api_url: str
    summary_stats: dict[
        str, float | int
    ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
    works_count: int

    alternate_titles: list[str | None] = field(default_factory=list)
    country_codes: list[str | None] = field(
        default_factory=list
    )  # ISO 3166-1 alpha-2 country code
    counts_by_year: list[YearCount | None] = field(default_factory=list)
    image_thumbnail_url: str | None = None
    image_url: str | None = None
    lineage: list[str | None] = field(default_factory=list)
    parent_publisher: str | None = None
    roles: list[Role | None] = field(default_factory=list)

    # UNDOCUMENTED FIELDS
    homepage_url: str | None = None


@dataclass
class Funder(BaseOpenAlex):
    cited_by_count: int
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    ids: FunderIds
    grants_count: int
    summary_stats: dict[
        str, float | int
    ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
    works_count: int
    alternate_titles: list[str | None] = field(default_factory=list)
    country_code: str | None = None
    counts_by_year: list[YearCount | None] = field(default_factory=list)
    description: str | None = None
    homepage_url: str | None = None
    image_thumbnail_url: str | None = None
    image_url: str | None = None
    roles: list[Role | None] = field(default_factory=list)


@dataclass
class Concept(BaseOpenAlex):
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    cited_by_count: int
    ids: ConceptIds
    level: int
    summary_stats: dict[str, float | int]
    wikidata: str
    works_api_url: str
    works_count: int

    counts_by_year: list[YearCount | None] = field(default_factory=list)
    description: str | None = None

    international: dict[Literal["display_name"], dict[str, str] | None] = field(
        default_factory=dict
    )
    related_concepts: list[DehydratedConcept | None] = field(default_factory=list)

    # UNDOCUMENTED FIELDS
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    ancestors: list[DehydratedConcept | None] = field(default_factory=list)


@dataclass
class Work(BaseOpenAlex):
    # core fields
    title: str
    publication_year: int
    publication_date: str  # YYYY-MM-DD
    created_date: str  # ISO 8601 date string
    updated_date: str  # ISO 8601 date string
    doi: str | None
    ids: WorkIds
    type: WorkType
    open_access: OpenAccess

    # bools
    has_fulltext: bool
    is_paratext: bool
    is_retracted: bool

    # counts
    locations_count: int
    cited_by_count: int
    countries_distinct_count: int
    institutions_distinct_count: int

    # UNDOCUMENTED FIELDS
    institution_assertions: list[str | None] = field(default_factory=list)
    cited_by_percentile_year: dict[str, int] = field(
        default_factory=dict
    )  # 'min' and 'max' keys
    datasets: list = field(default_factory=list)  # ?
    versions: list[str | None] = field(default_factory=list)  # ?
    referenced_works_count: int | None = None
    # nested fields
    abstract_inverted_index: dict[str, int] | None = None
    authorships: list[Authorship | None] = field(default_factory=list)
    apc_list: APCData | None = None
    apc_paid: APCData | None = None
    best_oa_location: Location | None = None
    biblio: Biblio | None = None
    citation_normalized_percentile: CitationNormalizedPercentile | None = None
    cited_by_api_url: str | None = None
    concepts: list[DehydratedConcept | None] = field(default_factory=list)
    corresponding_author_ids: list[str | None] = field(default_factory=list)
    corresponding_institution_ids: list[str | None] = field(default_factory=list)
    counts_by_year: list[YearCountBasic | None] = field(default_factory=list)
    fulltext_origin: Literal["pdf", "ngrams"] | None = None
    fwci: float | None = None
    grants: list[Grant | None] = field(default_factory=list)
    indexed_in: list[Literal["arxiv", "crossref", "doaj", "pubmed"] | None] = field(
        default_factory=list
    )
    keywords: list[DehydratedKeyword | None] = field(default_factory=list)
    language: str | None = None  # ISO 639-1 format
    license: str | None = None
    locations: list[Location | None] = field(default_factory=list)
    mesh: list[Mesh | None] = field(default_factory=list)
    primary_location: Location | None = None
    primary_topic: DehydratedTopic | None = None
    referenced_works: list[str | None] = field(default_factory=list)
    related_works: list[str | None] = field(default_factory=list)
    sustainable_development_goals: list[SDG | None] = field(default_factory=list)
    topics: list[DehydratedTopic | None] = field(default_factory=list)
    type_crossref: WorkTypeCrossref | None = None


# ----------------------------------------------------------------------------------------------------------------
# Response metadata and wrapper
# ----------------------------------------------------------------------------------------------------------------


@dataclass
class Meta:
    count: int
    db_response_time_ms: int
    page: int
    per_page: int
    groups_count: int | None = None


@dataclass
class PagedResponse:
    meta: Meta
    results: list[BaseOpenAlex | None] = field(default_factory=list)
