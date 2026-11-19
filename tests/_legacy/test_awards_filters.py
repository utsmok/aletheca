"""Tests for AwardsFilters — aliases must match the live API's valid-filter list.

The live API enumerates its valid filter fields in the 400 error it returns
for invalid ones; several filters modelled earlier (``funder.country_code``,
``lead_investigator.id``, ``co_lead_investigator.id``, plain ``funder``,
``from_/to_*_date``) are rejected by the API and were removed.
"""

from aletheca.endpoints import AwardsFilters

#: Valid dotted filter names from the live API's 400 error message
#: (https://api.openalex.org/awards?filter=funder.country_code:NL).
LIVE_VALID_FILTERS = {
    "amount",
    "collection",
    "currency",
    "default.search",
    "description.search",
    "display_name.search",
    "doi",
    "end_year",
    "funded_outputs",
    "funded_outputs_count",
    "funder.doi",
    "funder.id",
    "funder.ror",
    "funder_award_id",
    "funder_name",
    "funder_scheme",
    "funding_type",
    "id",
    "institution_awarded.continent",
    "institution_awarded.country_code",
    "institution_awarded.id",
    "institution_awarded.lineage",
    "institution_awarded.ror",
    "institution_awarded.type",
    "lead_investigator.affiliation.country",
    "lead_investigator.affiliation.name",
    "lead_investigator.family_name",
    "lead_investigator.given_name",
    "lead_investigator.orcid",
    "primary_topic.domain.id",
    "primary_topic.field.id",
    "primary_topic.id",
    "primary_topic.subfield.id",
    "provenance",
    "start_year",
    "text.search",
    "topics.domain.id",
    "topics.field.id",
    "topics.id",
    "topics.subfield.id",
}


def test_awards_filter_aliases_are_live_valid():
    """Every serialized alias must be a filter the live API accepts."""
    filters = AwardsFilters(
        id="G1",
        doi="https://doi.org/10.1234/x",
        funder_name="NSF",
        funder_award_id="123",
        funder_scheme="R01",
        funding_type="grant",
        provenance="nih_exporter",
        collection="c",
        currency="USD",
        end_year=2023,
        funded_outputs="W1|W2",
        funded_outputs_count=2,
        funder_id="F1",
        funder_ror="https://ror.org/x",
        funder_doi="https://doi.org/10.13039/x",
        lead_investigator_orcid="https://orcid.org/0000-0002-0000-0000",
        lead_investigator_given_name="A",
        lead_investigator_family_name="B",
        lead_investigator_affiliation_name="UT",
        lead_investigator_affiliation_country="NL",
        institution_awarded_id="I1",
        institution_awarded_ror="https://ror.org/y",
        institution_awarded_country_code="NL",
        institution_awarded_type="education",
        institution_awarded_lineage="I1",
        institution_awarded_continent="europe",
        primary_topic_id="T1",
        primary_topic_subfield_id="1",
        primary_topic_field_id="2",
        primary_topic_domain_id="3",
        topics_id="T2",
        topics_subfield_id="4",
        topics_field_id="5",
        topics_domain_id="6",
        display_name_search="dn",
        description_search="d",
        text_search="t",
        default_search="def",
    )
    serialized = filters.model_dump(exclude_none=True, by_alias=True)
    assert serialized, "nothing serialized"
    invalid = set(serialized) - LIVE_VALID_FILTERS
    assert not invalid, f"modelled filters the live API rejects: {sorted(invalid)}"


def test_awards_removed_invalid_filters_stay_out():
    """Filters the API 400s on must not be modelled (regression guard)."""
    fields = set(AwardsFilters.model_fields)
    for name in (
        "funder",
        "display_name",
        "funder_country_code",
        "lead_investigator_id",
        "co_lead_investigator_id",
        "from_awarded_date",
        "to_awarded_date",
        "from_created_date",
        "to_created_date",
        "from_updated_date",
        "to_updated_date",
    ):
        assert name not in fields, f"{name} was modelled but the live API rejects it"


def test_awards_filter_serialization_format():
    """Dotted aliases serialize to OpenAlex filter keys."""
    filters = AwardsFilters(funder_id="F4320321800", start_year=2020)
    serialized = filters.model_dump(exclude_none=True, by_alias=True)
    assert serialized == {"funder.id": "F4320321800", "start_year": 2020}
