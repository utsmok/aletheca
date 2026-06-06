"""Pydantic models for the Award entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import DehydratedTopic
from .safe_types import SafeList, SafeStr


class Award(BaseEntity):
    """An OpenAlex Award entity."""

    ids: dict | None = None

    # Core fields
    description: SafeStr | None = None
    doi: SafeStr | None = None
    funder_award_id: SafeStr | None = None
    funder: dict | None = None
    funding_type: SafeStr | None = None
    funder_scheme: SafeStr | None = None

    # Amount
    amount: float | None = None
    currency: SafeStr | None = None

    # Dates
    start_date: SafeStr | None = None
    start_year: int | None = None
    end_date: SafeStr | None = None
    end_year: int | None = None

    # People
    lead_investigator: dict | None = None
    co_lead_investigator: dict | None = None
    investigators: SafeList[dict] = Field(default_factory=list)

    # Outputs
    institution_awarded: dict | None = None
    funded_outputs: SafeList[str] = Field(default_factory=list)
    funded_outputs_count: int | None = None
    landing_page_url: SafeStr | None = None

    # Topics
    primary_topic: DehydratedTopic | None = None
    topics: SafeList[DehydratedTopic] = Field(default_factory=list)

    # Provenance
    provenance: dict | None = None

    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None

    model_config = ConfigDict(extra="allow")
