"""Endpoint path constants and Pydantic filter models for OpenAlex API."""

from pydantic import BaseModel, ConfigDict

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
    """

    publication_year: int | None = None
    publication_year_range: str | None = None
    publication_date: str | None = None
    publication_date_range: str | None = None
    type: str | None = None
    is_oa: bool | None = None
    open_access: str | None = None
    authorships_author_id: str | None = None
    authorships_institutions_id: str | None = None
    concepts_id: str | None = None
    topics_id: str | None = None
    primary_location_source_id: str | None = None
    primary_location_source_type: str | None = None
    doi: str | None = None
    pmid: str | None = None
    language: str | None = None
    cites: str | None = None
    cited_by: str | None = None
    related_to: str | None = None
    title: str | None = None
    title_search: str | None = None
    abstract_search: str | None = None
    default_search: str | None = None

    model_config = ConfigDict(extra="allow")


class AuthorsFilters(BaseModel):
    """Filter model for the Authors endpoint."""

    orcid: str | None = None
    display_name: str | None = None
    display_name_search: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None
    last_known_institution_id: str | None = None
    affiliation_institution_id: str | None = None
    topics_id: str | None = None
    x_concepts_id: str | None = None

    model_config = ConfigDict(extra="allow")


class SourcesFilters(BaseModel):
    """Filter model for the Sources endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
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

    model_config = ConfigDict(extra="allow")


class InstitutionsFilters(BaseModel):
    """Filter model for the Institutions endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
    country_code: str | None = None
    type: str | None = None
    ror: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None

    model_config = ConfigDict(extra="allow")


class TopicsFilters(BaseModel):
    """Filter model for the Topics endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
    id: str | None = None
    keywords_keyword: str | None = None
    subfield_id: str | None = None
    field_id: str | None = None
    domain_id: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    model_config = ConfigDict(extra="allow")


class KeywordsFilters(BaseModel):
    """Filter model for the Keywords endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
    keyword: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    model_config = ConfigDict(extra="allow")


class PublishersFilters(BaseModel):
    """Filter model for the Publishers endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
    country_codes: str | None = None
    hierarchy_level: int | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    model_config = ConfigDict(extra="allow")


class FundersFilters(BaseModel):
    """Filter model for the Funders endpoint."""

    display_name: str | None = None
    display_name_search: str | None = None
    country_code: str | None = None
    ror: str | None = None
    grants_count: int | None = None
    grants_count_range: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None

    model_config = ConfigDict(extra="allow")
