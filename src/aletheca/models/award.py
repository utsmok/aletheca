"""Pydantic models for the Award entity."""

from bibliofabric import SafeList, SafeStr
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import SDG, DehydratedKeyword, DehydratedTopic
from .dehydrated import DehydratedAuthor, DehydratedInstitution


class AwardFunder(BaseModel):
    """Funder reference on an award."""

    id: SafeStr | None = None
    display_name: SafeStr | None = None
    doi: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class InvestigatorAffiliation(BaseModel):
    """Affiliation of an award investigator."""

    name: SafeStr | None = None
    country: SafeStr | None = None
    ids: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class AwardInvestigator(BaseModel):
    """Investigator on an award (lead, co-lead, or listed investigator)."""

    given_name: SafeStr | None = None
    family_name: SafeStr | None = None
    orcid: SafeStr | None = None
    role_start: SafeStr | None = None
    affiliation: InvestigatorAffiliation | None = None
    author: DehydratedAuthor | None = None
    institutions: SafeList[DehydratedInstitution] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class Recipient(BaseModel):
    """Organisation receiving an award."""

    id: SafeStr | None = None
    display_name: SafeStr | None = None
    ror: SafeStr | None = None
    country_code: SafeStr | None = None
    roles: SafeList[str] = Field(default_factory=list)
    share: float | None = None
    basis: SafeStr | None = None
    asserted_by: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class RecipientCountry(BaseModel):
    """Per-country split of an award."""

    country_code: SafeStr | None = None
    share: float | None = None
    amount_usd: float | None = None
    basis: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class LinkedAward(BaseModel):
    """Parent or sub award linked to an award."""

    id: SafeStr | None = None
    display_name: SafeStr | None = None
    relationship: SafeStr | None = None
    asserted_by: SafeStr | None = None
    funder: AwardFunder | None = None

    model_config = ConfigDict(extra="allow")


class ResearchScope(BaseModel):
    """Research classification of an award."""

    is_research: bool | None = None
    basis: SafeStr | None = None
    tier: int | None = None

    model_config = ConfigDict(extra="allow")


class Award(BaseEntity):
    """An OpenAlex Award entity."""

    # Core fields
    description: SafeStr | None = None
    doi: SafeStr | None = None
    funder_award_id: SafeStr | None = None
    funder: AwardFunder | None = None
    funding_type: SafeStr | None = None
    funder_scheme: SafeStr | None = None

    # Amount
    amount: float | None = None
    amount_usd: float | None = None
    amount_usd_basis: SafeStr | None = None
    currency: SafeStr | None = None

    # Dates
    start_date: SafeStr | None = None
    start_year: int | None = None
    end_date: SafeStr | None = None
    end_year: int | None = None

    # People
    lead_investigator: AwardInvestigator | None = None
    co_lead_investigator: AwardInvestigator | None = None
    investigators: SafeList[AwardInvestigator] = Field(default_factory=list)
    recipients: SafeList[Recipient] = Field(default_factory=list)
    recipient_countries: SafeList[RecipientCountry] = Field(default_factory=list)
    # Element shape not yet observed (no populated probe or doc example found).
    recipient_regions: SafeList[dict] = Field(default_factory=list)

    # Linked awards
    sub_awards: SafeList[LinkedAward] = Field(default_factory=list)
    sub_awards_count: int | None = None
    parent_awards: SafeList[LinkedAward] = Field(default_factory=list)

    # Outputs and classification
    institution_awarded: SafeList[DehydratedInstitution] = Field(default_factory=list)
    funded_outputs: SafeList[str] = Field(default_factory=list)
    funded_outputs_count: int | None = None
    keywords: SafeList[DehydratedKeyword] = Field(default_factory=list)
    research_scope: ResearchScope | None = None
    sustainable_development_goals: SafeList[SDG] = Field(default_factory=list)
    landing_page_url: SafeStr | None = None

    # Topics
    primary_topic: DehydratedTopic | None = None
    topics: SafeList[DehydratedTopic] = Field(default_factory=list)

    # Provenance
    provenance: SafeStr | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
