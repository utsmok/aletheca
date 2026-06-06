"""Endpoint path constants and Pydantic filter models for OpenAlex API."""

from pydantic import BaseModel, ConfigDict, Field

# Endpoint paths
WORKS = "works"
AUTHORS = "authors"
SOURCES = "sources"
INSTITUTIONS = "institutions"
TOPICS = "topics"
KEYWORDS = "keywords"
PUBLISHERS = "publishers"
FUNDERS = "funders"


class WorksFilters(BaseModel):
    """Filter model for the Works endpoint.

    OpenAlex filter syntax: ``filter=field:value,field:value``
    Nested fields use dot notation via Pydantic aliases.
    """

    publication_year: int | None = None
    publication_date: str | None = None
    from_publication_date: str | None = Field(None, alias="from_publication_date")
    to_publication_date: str | None = Field(None, alias="to_publication_date")
    type: str | None = None
    is_oa: bool | None = None
    doi: str | None = None
    pmid: str | None = None
    language: str | None = None
    cites: str | None = None
    cited_by: str | None = None
    related_to: str | None = None

    # Nested filter fields (dot notation via alias)
    authorships_author_id: str | None = Field(None, alias="authorships.author.id")
    authorships_institutions_id: str | None = Field(
        None, alias="authorships.institutions.id"
    )
    concepts_id: str | None = Field(None, alias="concepts.id")
    topics_id: str | None = Field(None, alias="topics.id")
    primary_location_source_id: str | None = Field(
        None, alias="primary_location.source.id"
    )
    primary_location_source_type: str | None = Field(
        None, alias="primary_location.source.type"
    )
    primary_location_source_has_issn: bool | None = Field(
        None, alias="primary_location.source.has_issn"
    )
    primary_location_is_oa: bool | None = Field(None, alias="primary_location.is_oa")
    locations_is_oa: bool | None = Field(None, alias="locations.is_oa")
    locations_source_id: str | None = Field(None, alias="locations.source.id")
    locations_source_type: str | None = Field(None, alias="locations.source.type")

    # Search filters
    title_search: str | None = Field(None, alias="title.search")
    abstract_search: str | None = Field(None, alias="abstract.search")
    default_search: str | None = Field(None, alias="default.search")
    fulltext_search: str | None = Field(None, alias="fulltext.search")
    display_name_search: str | None = Field(None, alias="display_name.search")
    title_and_abstract_search: str | None = Field(
        None, alias="title_and_abstract.search"
    )
    raw_affiliation_strings_search: str | None = Field(
        None, alias="raw_affiliation_strings.search"
    )

    # Boolean presence filters
    has_doi: bool | None = Field(None, alias="has_doi")
    has_pmid: bool | None = Field(None, alias="has_pmid")
    has_pmcid: bool | None = Field(None, alias="has_pmcid")
    has_orcid: bool | None = Field(None, alias="has_orcid")
    has_abstract: bool | None = Field(None, alias="has_abstract")
    has_fulltext: bool | None = Field(None, alias="has_fulltext")
    has_references: bool | None = Field(None, alias="has_references")
    has_oa_accepted_or_published_version: bool | None = Field(
        None, alias="has_oa_accepted_or_published_version"
    )
    has_oa_submitted_version: bool | None = Field(
        None, alias="has_oa_submitted_version"
    )

    # Date range filters
    from_created_date: str | None = Field(None, alias="from_created_date")
    to_created_date: str | None = Field(None, alias="to_created_date")
    from_updated_date: str | None = Field(None, alias="from_updated_date")
    to_updated_date: str | None = Field(None, alias="to_updated_date")

    # Count / attribute filters
    authors_count: int | None = Field(None, alias="authors_count")
    best_oa_version: str | None = Field(None, alias="best_oa_version")
    version: str | None = Field(None, alias="version")
    # Additional common filters
    cited_by_count: str | None = None
    oa_status: str | None = None
    is_retracted: bool | None = Field(None, alias="is_retracted")
    is_paratext: bool | None = Field(None, alias="is_paratext")
    is_xpac: bool | None = Field(None, alias="is_xpac")
    referenced_works: str | None = Field(None, alias="referenced_works")
    locations_source_has_issn: bool | None = Field(None, alias="locations.source.has_issn")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class AuthorsFilters(BaseModel):
    """Filter model for the Authors endpoint."""

    orcid: str | None = None
    display_name: str | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    topics_id: str | None = Field(None, alias="topics.id")

    # Nested filter fields (dot notation via alias)
    affiliation_institution_id: str | None = Field(
        None, alias="affiliations.institution.id"
    )
    last_known_institutions_id: str | None = Field(
        None, alias="last_known_institutions.id"
    )
    x_concepts_id: str | None = Field(None, alias="x_concepts.id")

    # Search filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")

    # Boolean / presence filters
    has_orcid: bool | None = Field(None, alias="has_orcid")
    scopus: int | None = Field(None, alias="scopus")

    # Nested institution filters
    affiliations_institution_country_code: str | None = Field(
        None, alias="affiliations.institution.country_code"
    )
    affiliations_institution_lineage: str | None = Field(
        None, alias="affiliations.institution.lineage"
    )
    affiliations_institution_ror: str | None = Field(
        None, alias="affiliations.institution.ror"
    )
    affiliations_institution_type: str | None = Field(
        None, alias="affiliations.institution.type"
    )
    last_known_institutions_country_code: str | None = Field(
        None, alias="last_known_institutions.country_code"
    )
    last_known_institutions_lineage: str | None = Field(
        None, alias="last_known_institutions.lineage"
    )
    last_known_institutions_ror: str | None = Field(
        None, alias="last_known_institutions.ror"
    )
    last_known_institutions_type: str | None = Field(
        None, alias="last_known_institutions.type"
    )
    last_known_institutions_continent: str | None = Field(
        None, alias="last_known_institutions.continent"
    )
    last_known_institutions_is_global_south: bool | None = Field(
        None, alias="last_known_institutions.is_global_south"
    )

    # ID and summary stats filters
    ids_openalex: str | None = Field(None, alias="ids.openalex")
    summary_stats_2yr_mean_citedness: float | None = Field(
        None, alias="summary_stats.2yr_mean_citedness"
    )
    summary_stats_h_index: int | None = Field(None, alias="summary_stats.h_index")
    summary_stats_i10_index: int | None = Field(None, alias="summary_stats.i10_index")
    # Additional filters
    block_key: str | None = Field(None, alias="block_key")
    from_created_date: str | None = Field(None, alias="from_created_date")
    to_updated_date: str | None = Field(None, alias="to_updated_date")
    openalex: str | None = Field(None, alias="openalex")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class SourcesFilters(BaseModel):
    """Filter model for the Sources endpoint."""

    display_name: str | None = None
    type: str | None = None
    is_oa: bool | None = None
    host_organization: str | None = None
    issn: str | None = None
    issn_l: str | None = None
    has_apc: bool | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None

    # Search and additional filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")
    continent: str | None = Field(None, alias="continent")
    has_issn: bool | None = Field(None, alias="has_issn")
    is_global_south: bool | None = Field(None, alias="is_global_south")
    x_concepts_id: str | None = Field(None, alias="x_concepts.id")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class InstitutionsFilters(BaseModel):
    """Filter model for the Institutions endpoint."""

    display_name: str | None = None
    country_code: str | None = None
    type: str | None = None
    ror: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None

    # Search and additional filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")
    continent: str | None = Field(None, alias="continent")
    is_global_south: bool | None = Field(None, alias="is_global_south")
    has_ror: bool | None = Field(None, alias="has_ror")
    is_super_system: bool | None = Field(None, alias="is_super_system")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class TopicsFilters(BaseModel):
    """Filter model for the Topics endpoint."""

    display_name: str | None = None
    id: str | None = None
    subfield_id: str | None = None
    field_id: str | None = None
    domain_id: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    # Nested filter fields (dot notation via alias)
    display_name_search: str | None = Field(None, alias="display_name.search")
    keywords_search: str | None = Field(None, alias="keywords.search")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class KeywordsFilters(BaseModel):
    """Filter model for the Keywords endpoint."""

    display_name: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    # Search filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PublishersFilters(BaseModel):
    """Filter model for the Publishers endpoint."""

    display_name: str | None = None
    country_codes: str | None = None
    hierarchy_level: int | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    # Search filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")
    continent: str | None = Field(None, alias="continent")
    lineage: str | None = Field(None, alias="lineage")
    ror: str | None = Field(None, alias="ror")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class FundersFilters(BaseModel):
    """Filter model for the Funders endpoint."""

    display_name: str | None = None
    country_code: str | None = None
    ror: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    # Search filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    default_search: str | None = Field(None, alias="default.search")

    # Use awards_count (not grants_count)
    awards_count: int | None = Field(None, alias="awards_count")
    continent: str | None = Field(None, alias="continent")
    is_global_south: bool | None = Field(None, alias="is_global_south")

    model_config = ConfigDict(extra="allow", populate_by_name=True)
