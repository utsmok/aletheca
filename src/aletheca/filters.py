"""Pydantic filter models for the OpenAlex API.

Each model maps to the ``filter=field:value,field:value`` syntax of one
entity's list endpoint. Nested fields use dot-notation aliases. Every model
allows extra fields, so filters added upstream stay usable before they land
here.

Deprecated and paid filters are deliberately absent:

- ``concepts.id`` / ``x_concepts.id``: deprecated aliases of ``topics.id``.
- ``default.search``: alias of ``fulltext.search``.
- ``is_xpac`` / ``include_xpac``: legacy corpus controls; use the ``corpus``
  parameter (they 400 when combined with ``corpus=``).
- ``from/to_created_date``, ``from/to_updated_date`` on works: paid
  (Member+/Partner daily sync; free accounts get 403 "Plan upgrade required").
- ``is_in_jstage*`` on sources: no longer returned or documented upstream.
"""

from pydantic import BaseModel, ConfigDict, Field

_SharedConfig = ConfigDict(extra="allow", populate_by_name=True)


class WorksFilters(BaseModel):
    """Filter model for the works endpoint."""

    publication_year: int | None = None
    publication_date: str | None = None
    from_publication_date: str | None = None
    to_publication_date: str | None = None
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
    locations_source_has_issn: bool | None = Field(
        None, alias="locations.source.has_issn"
    )

    # Search filters. Deprecated upstream in favor of the ``search`` /
    # ``search.*`` parameters (see WorksClient.search_scoped); still served.
    title_search: str | None = Field(None, alias="title.search")
    abstract_search: str | None = Field(None, alias="abstract.search")
    fulltext_search: str | None = Field(None, alias="fulltext.search")
    display_name_search: str | None = Field(None, alias="display_name.search")
    title_and_abstract_search: str | None = Field(
        None, alias="title_and_abstract.search"
    )
    raw_affiliation_strings_search: str | None = Field(
        None, alias="raw_affiliation_strings.search"
    )

    # Boolean presence filters
    has_doi: bool | None = None
    has_pmid: bool | None = None
    has_pmcid: bool | None = None
    has_orcid: bool | None = None
    has_abstract: bool | None = None
    has_fulltext: bool | None = None
    has_references: bool | None = None
    has_oa_accepted_or_published_version: bool | None = Field(
        None, alias="has_oa_accepted_or_published_version"
    )
    has_oa_submitted_version: bool | None = Field(
        None, alias="has_oa_submitted_version"
    )

    # Count / attribute filters
    authors_count: int | None = None
    best_oa_version: str | None = None
    version: str | None = None
    cited_by_count: str | None = None
    oa_status: str | None = None
    is_retracted: bool | None = None
    is_paratext: bool | None = None
    referenced_works: str | None = None

    # Part-of (parent/child works) filters
    has_parent_work: bool | None = Field(None, alias="has_parent_work")
    parent_works_id: str | None = Field(None, alias="parent_works.id")
    parent_works_relationship: str | None = Field(
        None, alias="parent_works.relationship"
    )
    lineage: str | None = None
    child_works_count: str | None = None
    is_traditional: bool | None = None

    model_config = _SharedConfig


class AuthorsFilters(BaseModel):
    """Filter model for the authors endpoint."""

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
    display_name_search: str | None = Field(None, alias="display_name.search")

    # Boolean / presence filters
    has_orcid: bool | None = None

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
    block_key: str | None = None

    model_config = _SharedConfig


class SourcesFilters(BaseModel):
    """Filter model for the sources endpoint."""

    display_name: str | None = None
    type: str | None = None
    is_oa: bool | None = None
    host_organization: str | None = None
    issn: str | None = None
    issn_l: str | None = Field(None, alias="issn_l")
    has_apc: bool | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")
    continent: str | None = None
    has_issn: bool | None = None
    is_global_south: bool | None = None
    summary_stats_2yr_mean_citedness: float | None = Field(
        None, alias="summary_stats.2yr_mean_citedness"
    )
    summary_stats_h_index: int | None = Field(None, alias="summary_stats.h_index")
    summary_stats_i10_index: int | None = Field(None, alias="summary_stats.i10_index")

    model_config = _SharedConfig


class InstitutionsFilters(BaseModel):
    """Filter model for the institutions endpoint."""

    display_name: str | None = None
    country_code: str | None = None
    type: str | None = None
    ror: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    cited_by_count: int | None = None
    cited_by_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")
    continent: str | None = None
    is_global_south: bool | None = None
    has_ror: bool | None = None
    is_super_system: bool | None = None

    model_config = _SharedConfig


class TopicsFilters(BaseModel):
    """Filter model for the topics endpoint."""

    display_name: str | None = None
    id: str | None = None
    subfield_id: str | None = Field(None, alias="subfield.id")
    field_id: str | None = Field(None, alias="field.id")
    domain_id: str | None = Field(None, alias="domain.id")
    works_count: int | None = None
    works_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")
    keywords_search: str | None = Field(None, alias="keywords.search")
    keywords_id: str | None = Field(None, alias="keywords.id")
    keywords_keyword: str | None = Field(None, alias="keywords.keyword")
    keywords_display_name: str | None = Field(None, alias="keywords.display_name")

    model_config = _SharedConfig


class KeywordsFilters(BaseModel):
    """Filter model for the keywords endpoint."""

    display_name: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")

    model_config = _SharedConfig


class PublishersFilters(BaseModel):
    """Filter model for the publishers endpoint."""

    display_name: str | None = None
    country_codes: str | None = None
    hierarchy_level: int | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")
    continent: str | None = None
    lineage: str | None = None
    ror: str | None = None

    model_config = _SharedConfig


class FundersFilters(BaseModel):
    """Filter model for the funders endpoint."""

    display_name: str | None = None
    country_code: str | None = None
    ror: str | None = None
    works_count: int | None = None
    works_count_range: str | None = None
    display_name_search: str | None = Field(None, alias="display_name.search")
    awards_count: int | None = None
    continent: str | None = None
    is_global_south: bool | None = None
    summary_stats_2yr_mean_citedness: float | None = Field(
        None, alias="summary_stats.2yr_mean_citedness"
    )
    summary_stats_h_index: int | None = Field(None, alias="summary_stats.h_index")
    summary_stats_i10_index: int | None = Field(None, alias="summary_stats.i10_index")

    model_config = _SharedConfig


class AwardsFilters(BaseModel):
    """Filter model for the awards endpoint.

    Aliases follow the live API's valid-filter list, which the API
    enumerates in the 400 error returned for invalid fields.
    ``funder.country_code``, ``lead_investigator.id``,
    ``co_lead_investigator.id``, plain ``funder`` and ``display_name``,
    and ``from_/to_*_date`` range filters are NOT valid on this endpoint
    and are absent here; ``extra="allow"`` still lets callers pass
    anything else.
    """

    id: str | None = None
    doi: str | None = None
    funder_name: str | None = None
    funder_award_id: str | None = None
    funder_scheme: str | None = None
    funding_type: str | None = None
    provenance: str | None = None
    collection: str | None = None
    currency: str | None = None
    amount: float | None = None
    start_year: int | None = None
    end_year: int | None = None
    funded_outputs: str | None = None
    funded_outputs_count: int | None = None

    # Nested filter fields (dot notation via alias)
    funder_id: str | None = Field(None, alias="funder.id")
    funder_ror: str | None = Field(None, alias="funder.ror")
    funder_doi: str | None = Field(None, alias="funder.doi")
    lead_investigator_orcid: str | None = Field(None, alias="lead_investigator.orcid")
    lead_investigator_given_name: str | None = Field(
        None, alias="lead_investigator.given_name"
    )
    lead_investigator_family_name: str | None = Field(
        None, alias="lead_investigator.family_name"
    )
    lead_investigator_affiliation_name: str | None = Field(
        None, alias="lead_investigator.affiliation.name"
    )
    lead_investigator_affiliation_country: str | None = Field(
        None, alias="lead_investigator.affiliation.country"
    )
    institution_awarded_id: str | None = Field(None, alias="institution_awarded.id")
    institution_awarded_ror: str | None = Field(None, alias="institution_awarded.ror")
    institution_awarded_country_code: str | None = Field(
        None, alias="institution_awarded.country_code"
    )
    institution_awarded_type: str | None = Field(None, alias="institution_awarded.type")
    institution_awarded_lineage: str | None = Field(
        None, alias="institution_awarded.lineage"
    )
    institution_awarded_continent: str | None = Field(
        None, alias="institution_awarded.continent"
    )
    primary_topic_id: str | None = Field(None, alias="primary_topic.id")
    primary_topic_subfield_id: str | None = Field(
        None, alias="primary_topic.subfield.id"
    )
    primary_topic_field_id: str | None = Field(None, alias="primary_topic.field.id")
    primary_topic_domain_id: str | None = Field(None, alias="primary_topic.domain.id")
    topics_id: str | None = Field(None, alias="topics.id")
    topics_subfield_id: str | None = Field(None, alias="topics.subfield.id")
    topics_field_id: str | None = Field(None, alias="topics.field.id")
    topics_domain_id: str | None = Field(None, alias="topics.domain.id")

    # Search filters
    display_name_search: str | None = Field(None, alias="display_name.search")
    description_search: str | None = Field(None, alias="description.search")
    text_search: str | None = Field(None, alias="text.search")

    model_config = _SharedConfig
