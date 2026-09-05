"""Pydantic models for dehydrated (partial) entity representations."""

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .safe_types import SafeList, SafeStr


class DehydratedAuthor(BaseEntity):
    """Minimal author info embedded in authorships."""

    orcid: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class DehydratedInstitution(BaseEntity):
    """Minimal institution info embedded in other entities."""

    country_code: SafeStr | None = None
    ror: SafeStr | None = None
    type: str | None = None
    lineage: SafeList[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class RelatedInstitution(DehydratedInstitution):
    """Dehydrated institution with relationship type."""

    relationship: str | None = None


class DehydratedInstitutionWithYear(BaseModel):
    """Institution with years of affiliation."""

    institution: DehydratedInstitution | None = None
    years: SafeList[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class SimpleDehydratedConcept(BaseEntity):
    """Minimal concept info (deprecated entity)."""

    level: int | None = None
    wikidata: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class DehydratedConcept(SimpleDehydratedConcept):
    """Concept with relevance score (deprecated entity)."""

    score: float = 0.0

    model_config = ConfigDict(extra="allow")
