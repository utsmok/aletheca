import marimo

__generated_with = "0.17.8"
app = marimo.App(
    width="columns",
    layout_file="layouts/check_entity_dataclasses.grid.json",
)


@app.cell(hide_code=True)
def _(Author, Concept, Funder, Institution, Publisher, Source, Topic, Work):
    import httpx
    from rich import print
    from rich.pretty import Pretty
    from collections import defaultdict
    import marimo as mo

    mapping = {
        "work": Work,
        "author": Author,
        "source": Source,
        "topic": Topic,
        "concept": Concept,
        "publisher": Publisher,
        "institution": Institution,
        "funder": Funder,
    }
    return Pretty, defaultdict, httpx, mapping, mo, print


@app.cell(hide_code=True)
def _(mapping, mo):
    new_sample = mo.ui.run_button(kind="success", label="🔄️ Click to refresh API data.")
    selection = mo.ui.multiselect(
        options=list(mapping.keys()), label="Select entity types to fetch", value=list(mapping.keys())
    )
    num_to_retrieve = mo.ui.number(label="Number of entities to retrieve per type", value=50, start=1, stop=100)
    mo.vstack([selection, num_to_retrieve, new_sample])
    return new_sample, num_to_retrieve, selection


@app.cell(hide_code=True)
def _(httpx, mo, new_sample, num_to_retrieve, print, selection):
    if new_sample.value:
        base_url = "https://api.openalex.org/"
        data = {}
        with httpx.Client() as client:
            for ent_type in mo.status.progress_bar(
                selection.value,
                title="Fetching example data from the OpenAlex API",
            ):
                try:
                    data[ent_type] = client.get(f"{base_url}{ent_type}s?sample={num_to_retrieve.value}&per-page=100").json()
                except Exception as e:
                    print(f"Error fetching {ent_type}: {e}")
    return (data,)


@app.cell(hide_code=True)
def _(Pretty, error_data, mo, num_to_retrieve, parsed_data, print):
    output = [mo.md("## No data retrieved yet. Click the green button above!")]
    show2 = mo.md("")
    msg2 = mo.md("## No parsing errors! 🥳")
    n = 0
    msg = ""
    if parsed_data:
    
        tab_data = {}
        for res_type, parsed_result in parsed_data.items():
            tab_name = str(res_type)
            left_col = []
            right_col = []
            if len(parsed_result) > 2:
                parsed_result = parsed_result[:2]

            for itemduo in parsed_result:
                left_col.append(Pretty(itemduo[0]))
                right_col.append(Pretty(itemduo[1]))
            tab_data[tab_name] = mo.vstack([mo.md(f'## {len(parsed_result)}/{num_to_retrieve.value} entries shown below.'), mo.hstack([          
                mo.vstack([mo.md("Raw API data (dict)")] + left_col),
                mo.vstack([mo.md("Parsed as nested dataclass")] + right_col),
            ])])
            print(f"{tab_name}: {len(parsed_result)} parsed entries, {len(left_col)} left col entries, {len(right_col)} right col entries")
        print(len(tab_data))
        show = mo.ui.tabs(tab_data)

    
        if error_data:
            msg += "Note: some entities failed to parse. See table below."
            msg2 = mo.md("## Entity entries that failed to parse")
            show2 = mo.vstack(
                [
                    mo.ui.tabs(
                        {
                            str(res_type).capitalize(): mo.hstack(
                                [
                                    mo.vstack(
                                        [mo.md("Raw API data (dict)"), Pretty(parsed_result[0][0])]
                                    ),
                                    mo.vstack(
                                        [
                                            mo.md("Errors:"),
                                            parsed_result[0][1]
                                        ]
                                    ),
                                ]
                            )
                            for res_type, parsed_result in error_data.items()
                        }
                    )
                ]
            )
        output = [mo.md(msg), show]

    mo.vstack(output)
    return msg2, show2


@app.cell
def _(mo, msg2, show2):
    mo.vstack([msg2, show2])
    return


@app.cell(hide_code=True)
def _(Response, data, defaultdict, mapping, mo, new_sample, print):
    errors = []
    wrong_data = {}
    parsed_data = defaultdict(list)
    error_data = defaultdict(list)
    if new_sample.value:
        errors = []
        for ent, response in data.items():
            entity_class = mapping[ent]
            try:
                ent_response = Response.from_dict(response, result_type=entity_class)
                list_of_results = ent_response.results
            except Exception as e:
                # parse each set individually and collect errors
                list_of_results = []
                for ent_num, raw_data in enumerate(response.get("results", [])):
                    try:
                        ent_data = entity_class.from_dict(raw_data)
                        list_of_results.append(ent_data)
                    except Exception as inner_e:
                        print(f"Error parsing individual {ent} entity number {ent_num}: {inner_e}")
                        list_of_results.append(None)
                        error_data["❌ " + ent].append(
                            [raw_data, mo.md(f"⚠️ Error! ----- {inner_e}")]
                        )
            for ent_data, raw_data in zip(list_of_results, response.get("results")):
                if not ent_data:
                    parsed_data["✅ " + ent].append([raw_data, mo.md("⚠️ Failed to parse entity See table below for details.")])
                parsed_data["✅ " + ent].append([raw_data, ent_data])
    return error_data, parsed_data


@app.cell
def _():
    """

    dataclasses to represent data retrieved from OpenAlex

    based on the official docs: https://docs.openalex.org/api-entities/

    """

    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Generic, Literal, Self, TypeVar

    from dacite import Config, from_dict

    default_dacite_config = Config(strict=True)
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
        "funder",  # NOTE: NOT documented in OpenAlex docs, but appears in data
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

        # openalex id -- SOMETIMES THIS IS null for dehydrated entities?? e.g. in authorships for https://openalex.org/W7104996979
        id: str | None

        # these fields below are all marked as optional -- but probably should not be in practice??

        # can be none, e.g. for works sometimes https://openalex.org/W4386670207
        display_name: str | None

        # dunno what this is doing in the response -- got this when using the random sample query (?sample=10)
        relevance_score: float | None

        # !! found missing creation/updated dates in api data, e.g. https://openalex.org/P4361727468. Should probably be non-nullable, could always default to created_date
        created_date: str | None
        updated_date: str | None

        # not documented? often missing?
        score: float | None

        cited_by_count: int | None
        works_count: int | None
        works_api_url: str | None

        @classmethod
        def from_dict(cls, data: dict) -> Self:
            return from_dict(data_class=cls, data=data, config=default_dacite_config)


    # ----------------------------------------------------------------------------------------------------------------
    #  Nested fields
    # ----------------------------------------------------------------------------------------------------------------


    @dataclass
    class WorkIds:
        openalex: str
        doi: str | None
        mag: int | str | None
        pmid: str | None
        pmcid: str | None


    @dataclass
    class AuthorIds:
        openalex: str
        orcid: str | None
        scopus: str | None
        twitter: str | None
        wikipedia: str | None


    @dataclass
    class SourceIds:
        openalex: str
        fatcat: str | None
        issn: list[str | None] | None
        issn_l: str | None
        mag: int | str | None
        wikidata: str | None


    @dataclass
    class InstitutionIds:
        openalex: str
        ror: str | None
        grid: str | None
        mag: int | str | None
        wikidata: str | None
        wikipedia: str | None


    @dataclass
    class TopicIds:
        openalex: str
        wikipedia: str | None


    @dataclass
    class PublisherIds:
        openalex: str
        ror: str | None
        wikidata: str | None


    @dataclass
    class FunderIds:
        openalex: str
        doi: str | None
        crossref: str | None
        ror: str | None
        wikidata: str | None


    @dataclass
    class ConceptIds:
        openalex: str
        mag: int | str | None
        umls_cui: list[str] | None
        umls_aui: list[str] | None
        wikidata: str | None
        wikipedia: str | None


    @dataclass
    class Affiliation:
        raw_affiliation_string: str
        institution_ids: list[str | None]


    @dataclass
    class DehydratedAuthor(BaseOpenAlex):
        orcid: str | None


    @dataclass
    class DehydratedInstitution(BaseOpenAlex):
        country_code: str | None  # ISO 3166-1 alpha-2 country code
        lineage: list[str | None] | None
        ror: str | None
        type: InstitutionType | None


    @dataclass
    class RelatedInstitution(DehydratedInstitution):
        # undocumented value found: "successor"
        relationship: Literal["parent", "child", "related", "successor"] | None


    @dataclass
    class DehydratedInstitutionWithYear:
        institution: DehydratedInstitution
        years: list[int | None]


    @dataclass
    class DehydratedSource(BaseOpenAlex):
        is_core: bool
        is_in_doaj: bool
        is_oa: bool
        # undocumented field!! Also not always present, so nullable bool-type :(
        is_indexed_in_scopus: bool | None
        type: SourceType
        issn_l: str | None
        issn: list[str] | None
        host_organization: str | None
        host_organization_lineage: list[str | None]
        host_organization_name: str | None
        # undocumented field!!
        host_organization_lineage_names: list[str | None] | None
        raw_type: (
            str | None
        )  # undocumented field!! e.g. 'journal-article', ex. https://openalex.org/W4382601591


    @dataclass
    class Repository(BaseOpenAlex):
        # specific field for the 'repositories' field of Institution entity
        host_organization: str | None
        host_organization_lineage: list[str | None]
        host_organization_name: str | None


    @dataclass
    class SimpleDehydratedConcept(BaseOpenAlex):
        # field is sometimes missing? happened for author in the x_concept field, here: https://openalex.org/A5011476733
        level: int | None
        wikidata: str | None


    @dataclass
    class DehydratedConcept(SimpleDehydratedConcept):
        score: float


    @dataclass
    class Authorship:
        author: DehydratedAuthor
        raw_author_name: str
        is_corresponding: bool
        countries: list[str]
        author_position: Literal["first", "middle", "last"] | None
        affiliations: list[Affiliation]
        institutions: list[DehydratedInstitution]
        raw_affiliation_strings: list[str]


    @dataclass
    class APCData:
        value: int | None
        currency: str | None
        value_usd: int | None
        provenance: str | None


    @dataclass
    class APCEntry:
        price: int
        currency: str


    @dataclass
    class Biblio:
        volume: str | None
        issue: str | None
        first_page: str | None
        last_page: str | None


    @dataclass
    class Mesh:
        descriptor_ui: str
        descriptor_name: str
        is_major_topic: bool
        qualifier_ui: str | None
        qualifier_name: str | None


    @dataclass
    class Location:
        is_accepted: (
            bool | None
        )  # should not be None, but data from Datacite API does not have this field apparently
        is_oa: bool
        is_published: (
            bool | None
        )  # sometimes none?? e.g. in the locations of https://openalex.org/W2939702801
        landing_page_url: str | None
        pdf_url: str | None
        license: str | None
        license_id: str | None  # undocumented field!!

        source: DehydratedSource | None
        version: Literal["publishedVersion", "acceptedVersion", "submittedVersion"] | None

        raw_source_name: (
            str | None
        )  # undocumented field!! see https://openalex.org/W1980689546
        id: (
            str | None
        )  # undocumented field!! e.g. 'doi:10.1115/pvp2009-77064', from same example as above


    @dataclass
    class OpenAccess:
        is_oa: bool
        oa_status: Literal["diamond", "gold", "green", "hybrid", "bronze", "closed"]
        oa_url: str | None
        any_repository_has_fulltext: bool


    @dataclass
    class Grant:
        funder: str | None
        funder_display_name: str | None
        award_id: str | None


    # UNDOCUMENTED! work.funders field is a list of these?
    @dataclass
    class DehydratedFunder:
        id: str | None  # openalex id of the funder
        display_name: str | None  # name of the funder
        ror: str | None  # ror id of the funder


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
        score: float | None  # not documented? often missing?
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
        score: float


    @dataclass
    class CitationNormalizedPercentile:
        value: float
        is_in_top_1_percent: bool
        is_in_top_10_percent: bool


    @dataclass
    class YearCountBasic:
        year: int | None
        cited_by_count: int | None


    @dataclass
    class YearCount:
        year: int | None
        cited_by_count: int | None
        works_count: int | None
        oa_works_count: int | None  # undocumented field!!


    @dataclass
    class SummaryStats:
        """
        This class is not used directly:
        the actual fieldname in OpenAlex is "2yr_mean_citedness" but we cannot use that as an attribute name in Python.
        Instead, the summary_stats field in entities uses a dict[str, float | int] for now.
        In the future, we can implement custom parsing logic to map this field properly, or use a library like pydantic that supports aliasing.
        """

        two_yr_mean_citedness: float  # actual name: "2yr_mean_citedness"
        h_index: int
        i10_index: int


    @dataclass
    class Society:
        url: str | None
        organization: str | None


    @dataclass
    class Geo:
        city: str | None
        geonames_city_id: str | None
        region: str | None
        country_code: str | None  # ISO 3166-1 alpha-2 country code
        country: str | None
        latitude: float | None
        longitude: float | None


    @dataclass
    class Role:
        role: Literal["funder", "publisher", "institution"]
        id: str
        works_count: int | None


    @dataclass
    class International:
        """
        Container for localized display labels in OpenAlex.

        Example shape in OpenAlex:
        {
            "display_name": {"en": "Example", "fr": "Exemple"},
            "description": {"en": "desc", "fr": "desc_fr"}
        }

        """

        display_name: dict[str, str] | None
        description: dict[str, str] | None  # this 'description' key is undocumented!


    @dataclass
    class HasContent:  # undocumented field for Work entity?
        pdf: bool
        grobid_xml: bool


    # ----------------------------------------------------------------------------------------------------------------
    # Main entities
    # ----------------------------------------------------------------------------------------------------------------


    @dataclass
    class Keyword(BaseOpenAlex): ...


    @dataclass
    class Topic(BaseOpenAlex):
        description: str
        ids: TopicIds
        keywords: list[str]
        subfield: Subfield
        field: Field
        domain: Domain
        siblings: list[TopicMinimal]


    @dataclass
    class Author(BaseOpenAlex):
        ids: AuthorIds
        orcid: str | None

        summary_stats: dict[
            str, float | int
        ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness

        affiliations: list[DehydratedInstitutionWithYear | None]
        counts_by_year: list[YearCount | None]
        display_name_alternatives: list[str | None]
        last_known_institutions: list[DehydratedInstitution | None]
        x_concepts: list[DehydratedConcept | None]

        # UNDOCUMENTED FIELDS
        topics: list[TopicCount | None]
        topic_share: list[TopicShare | None]


    @dataclass
    class Source(BaseOpenAlex):
        ids: SourceIds
        is_core: bool
        is_in_doaj: bool
        is_oa: bool
        summary_stats: dict[
            str, float | int
        ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
        type: SourceType

        abbreviated_title: str | None
        alternate_titles: list[str | None] | None
        apc_prices: list[APCEntry | None] | None
        apc_usd: int | None
        country_code: str | None  # ISO 3166-1 alpha-2 country code
        counts_by_year: list[YearCount | None]
        homepage_url: str | None
        host_organization: str | None
        host_organization_lineage: list[str | None]
        host_organization_name: str | None
        issn: list[str | None] | None
        issn_l: str | None
        societies: list[Society | None] | None
        # sometimes missing, e.g. https://openalex.org/S4210223070
        x_concepts: list[DehydratedConcept | None] | None

        # UNDOCUMENTED FIELDS
        is_indexed_in_scopus: bool | None
        topics: list[TopicCount | None]
        topic_share: list[TopicShare | None]
        relevance_score: float | None
        oa_flip_year: int | None
        is_high_oa_rate: bool | None
        is_ojs: bool | None
        is_in_scielo: bool | None
        is_high_oa_rate_since_year: int | None
        is_in_doaj_since_year: int | None
        oa_works_count: int | None
        last_publication_year: int | None
        first_publication_year: int | None


    @dataclass
    class Institution(BaseOpenAlex):
        ids: InstitutionIds
        is_super_system: bool
        summary_stats: dict[
            str, float | int
        ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
        type: InstitutionType

        associated_institutions: list[RelatedInstitution | None] | None
        country_code: str | None  # ISO 3166-1 alpha-2 country code
        counts_by_year: list[YearCount | None]
        display_name_acronyms: list[str | None]
        display_name_alternatives: list[str | None]
        geo: Geo | None
        homepage_url: str | None
        image_thumbnail_url: str | None
        image_url: str | None
        international: International | None

        lineage: list[str | None] | None

        repositories: list[Repository | None]
        roles: list[Role | None]
        ror: str | None

        # sometimes missing, e.g. https://openalex.org/I4210128891
        x_concepts: list[DehydratedConcept | None] | None

        # UNDOCUMENTED FIELDS
        type_id: str | None
        topics: list[TopicCount | None]
        topic_share: list[TopicShare | None]


    @dataclass
    class Publisher(BaseOpenAlex):
        hierarchy_level: (
            int | None
        )  # !! found 'None' value in api data, e.g. https://openalex.org/P4404660908
        ids: PublisherIds
        sources_api_url: str
        summary_stats: (
            dict[str, float | int] | None
        )  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
        # also, seems to be missing sometimes? e.g. https://openalex.org/P4310316202

        alternate_titles: list[str | None]
        country_codes: (
            list[str | None] | None
        )  # sometimes missing, e.g. https://openalex.org/P4361730451

        counts_by_year: list[YearCount | None]
        image_thumbnail_url: str | None
        image_url: str | None

        # sometimes missing, see https://openalex.org/P4320800631
        lineage: list[str | None] | None

        # !! undocumented value: not just the name -- but a dict with 'id' and 'display_name' keys!
        parent_publisher: BaseOpenAlex | None

        # sometimes missing completely, e.g. https://openalex.org/P4376884348
        roles: list[Role | None] | None

        # UNDOCUMENTED FIELDS
        homepage_url: str | None


    @dataclass
    class Funder(BaseOpenAlex):
        ids: FunderIds
        grants_count: int
        summary_stats: dict[
            str, float | int | None
        ]  # see SummaryStats -- cannot use directly due to naming issue with 2yr_mean_citedness
        # had to add | None because sometimes one of the stats is null, e.g. https://openalex.org/F4320319847
        alternate_titles: list[str | None]
        country_code: str | None
        counts_by_year: list[YearCount | None]
        description: str | None
        homepage_url: str | None
        image_thumbnail_url: str | None
        image_url: str | None
        roles: list[Role | None]


    @dataclass
    class Concept(BaseOpenAlex):
        ids: ConceptIds
        level: int
        summary_stats: dict[str, float | int] | None  # seems to be empty?
        wikidata: str

        counts_by_year: list[YearCount | None] | None  # seems to be empty?
        description: str | None

        international: International | None

        # !! Related concepts have 'wikidata' == None, shouldn't happen!
        # also, if empty, is None instead of [], e.g. https://openalex.org/C65148998

        related_concepts: list[DehydratedConcept | None] | None

        # UNDOCUMENTED FIELDS
        image_url: str | None
        image_thumbnail_url: str | None

        # sometimes empty (null) even though not level 0, e.g. https://openalex.org/C94727143
        ancestors: list[SimpleDehydratedConcept | None] | None


    @dataclass
    class Work(BaseOpenAlex):
        # core fields
        title: str | None
        publication_year: int
        publication_date: str  # YYYY-MM-DD
        doi: str | None
        ids: WorkIds
        type: WorkType
        open_access: OpenAccess

        # bools
        # should never be None, but got results with this missing, e.g. https://openalex.org/W3028709719

        has_fulltext: bool | None
        is_paratext: bool
        is_retracted: bool

        # counts
        locations_count: int
        cited_by_count: int
        countries_distinct_count: int
        institutions_distinct_count: int

        # UNDOCUMENTED FIELDS
        # examples with these fields: https://openalex.org/W2024107613
        institution_assertions: list[str | None] | None
        funders: list[DehydratedFunder | None] | None
        institutions: list[DehydratedInstitution | None] | None
        is_xpac: bool | None
        awards: list[str | None] | None

        # nested fields
        abstract_inverted_index: dict[str, list[int]] | None
        authorships: list[Authorship | None]
        apc_list: APCData | None
        apc_paid: APCData | None
        best_oa_location: Location | None
        biblio: Biblio | None
        citation_normalized_percentile: CitationNormalizedPercentile | None
        cited_by_api_url: str | None
        concepts: list[DehydratedConcept | None]
        corresponding_author_ids: list[str | None]
        corresponding_institution_ids: list[str | None]
        counts_by_year: list[YearCountBasic | None]
        fulltext_origin: Literal["pdf", "ngrams"] | None
        fwci: float | None
        grants: list[Grant | None]
        indexed_in: list[
            Literal["arxiv", "crossref", "doaj", "pubmed", "datacite"] | None
        ]  # !! datacite is undocumented!
        keywords: list[DehydratedKeyword | None]
        language: str | None
        license: str | None
        locations: list[Location | None]
        mesh: list[Mesh | None]
        primary_location: Location | None
        primary_topic: DehydratedTopic | None
        referenced_works: list[str | None]
        related_works: list[str | None]
        sustainable_development_goals: list[SDG | None]
        topics: list[DehydratedTopic | None]
        type_crossref: WorkTypeCrossref | None
        has_content: HasContent | None

        # is none when publication_year == current year apparently
        cited_by_percentile_year: dict[str, int] | None
        datasets: list | None  # ?
        versions: list[str | None] | None  # ?
        referenced_works_count: int | None


    # ----------------------------------------------------------------------------------------------------------------
    # Response metadata and wrapper
    # ----------------------------------------------------------------------------------------------------------------
    T = TypeVar("T", bound=BaseOpenAlex)


    @dataclass
    class Meta:
        count: int
        db_response_time_ms: int
        page: int
        per_page: int
        groups_count: int | None
        next_cursor: str | None

        @classmethod
        def from_dict(cls, data: dict) -> Meta:
            return from_dict(data_class=cls, data=data, config=default_dacite_config)


    @dataclass
    class Response(Generic[T]):
        meta: Meta
        results: list[T | None]

        @classmethod
        def from_dict(cls, data: dict, result_type: type[T] | None) -> "Response[T]":
            raw_meta = data.get("meta")
            if raw_meta is None:
                raise ValueError("Missing 'meta' field in response data")
            meta = Meta.from_dict(raw_meta)
            raw_results = data.get("results", [])
            if result_type:
                parsed = [
                    None
                    if r is None
                    else from_dict(
                        data_class=result_type, data=r, config=default_dacite_config
                    )
                    for r in raw_results
                ]
                return cls(meta=meta, results=parsed)  # pyright: ignore[reportArgumentType]
            return from_dict(data_class=cls, data=data, config=default_dacite_config)

    return (
        Author,
        Concept,
        Funder,
        Institution,
        Publisher,
        Response,
        Source,
        Topic,
        Work,
    )


if __name__ == "__main__":
    app.run()
