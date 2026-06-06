"""Pydantic models for OpenAlex entity ID objects."""

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .safe_types import SafeList, SafeStr


class WorkIds(BaseModel):
    """IDs for a Work entity."""

    openalex: SafeStr = ""
    doi: SafeStr | None = None
    mag: int | str | None = None
    pmid: SafeStr | None = None
    pmcid: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class AuthorIds(BaseModel):
    """IDs for an Author entity."""

    openalex: SafeStr = ""
    orcid: SafeStr | None = None
    scopus: SafeStr | None = None
    twitter: SafeStr | None = None
    wikipedia: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class SourceIds(BaseModel):
    """IDs for a Source entity."""

    openalex: SafeStr = ""
    issn: SafeList[str] = Field(default_factory=list)
    issn_l: SafeStr | None = None
    mag: int | str | None = None
    wikidata: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class InstitutionIds(BaseModel):
    """IDs for an Institution entity."""

    openalex: SafeStr = ""
    ror: SafeStr | None = None
    grid: SafeStr | None = None
    mag: int | str | None = None
    wikidata: SafeStr | None = None
    wikipedia: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class TopicIds(BaseModel):
    """IDs for a Topic entity."""

    openalex: SafeStr = ""
    wikipedia: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class PublisherIds(BaseModel):
    """IDs for a Publisher entity."""

    openalex: SafeStr = ""
    ror: SafeStr | None = None
    wikidata: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class FunderIds(BaseModel):
    """IDs for a Funder entity."""

    openalex: SafeStr = ""
    doi: SafeStr | None = None
    crossref: SafeStr | None = None
    ror: SafeStr | None = None
    wikidata: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class ConceptIds(BaseModel):
    """IDs for a Concept entity (deprecated)."""

    openalex: SafeStr = ""
    mag: int | str | None = None
    umls_cui: SafeList[str] = Field(default_factory=list)
    umls_aui: SafeList[str] = Field(default_factory=list)
    wikidata: SafeStr | None = None
    wikipedia: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
