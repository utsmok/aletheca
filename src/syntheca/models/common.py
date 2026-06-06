"""Shared Pydantic models for common nested types across OpenAlex entities."""

from typing import Literal

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .safe_types import SafeList, SafeStr

# --- APC (Article Processing Charge) ---


class APCEntry(BaseModel):
    """A single APC price entry."""

    price: int = 0
    currency: SafeStr = ""

    model_config = ConfigDict(extra="allow")


class APCData(BaseModel):
    """APC data for a source."""

    value: int | None = None
    currency: SafeStr | None = None
    value_usd: int | None = None
    provenance: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


# --- Bibliographic ---


class Biblio(BaseModel):
    """Bibliographic metadata (volume, issue, pages)."""

    volume: SafeStr | None = None
    issue: SafeStr | None = None
    first_page: SafeStr | None = None
    last_page: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class Mesh(BaseModel):
    """MeSH term attached to a work."""

    descriptor_ui: SafeStr = ""
    descriptor_name: SafeStr = ""
    is_major_topic: bool = False
    qualifier_ui: SafeStr | None = None
    qualifier_name: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


# --- Location ---


class Location(BaseModel):
    """A location where a work can be found."""

    is_accepted: bool | None = None
    is_oa: bool = False
    is_published: bool | None = None
    landing_page_url: SafeStr | None = None
    pdf_url: SafeStr | None = None
    license: SafeStr | None = None
    license_id: SafeStr | None = None
    source: dict | None = None  # DehydratedSource — set in work.py
    version: (
        Literal["publishedVersion", "acceptedVersion", "submittedVersion"] | None
    ) = None
    raw_source_name: SafeStr | None = None
    id: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


# --- Open Access ---


class OpenAccess(BaseModel):
    """Open access status of a work."""

    is_oa: bool = False
    oa_status: Literal[
        "diamond", "gold", "green", "hybrid", "bronze", "closed"
    ] | None = None
    oa_url: SafeStr | None = None
    any_repository_has_fulltext: bool = False

    model_config = ConfigDict(extra="allow")


# --- Funder (nested) ---


class DehydratedFunder(BaseModel):
    """Minimal funder info embedded in works."""

    id: SafeStr | None = None
    display_name: SafeStr | None = None
    ror: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


# --- Topic hierarchy (minimal) ---


class Domain(BaseEntity):
    """A topic domain."""

    model_config = ConfigDict(extra="allow")


class FieldEntity(BaseEntity):
    """A topic field."""

    model_config = ConfigDict(extra="allow")


class Subfield(BaseEntity):
    """A topic subfield."""

    model_config = ConfigDict(extra="allow")


class TopicMinimal(BaseEntity):
    """Minimal topic representation."""

    model_config = ConfigDict(extra="allow")


class DehydratedTopic(BaseEntity):
    """Topic with score, embedded in other entities."""

    score: float = 0.0
    subfield: Subfield | None = None
    field: FieldEntity | None = None
    domain: Domain | None = None

    model_config = ConfigDict(extra="allow")


class TopicCount(BaseEntity):
    """Topic with count and score."""

    count: int = 0
    score: float | None = None
    subfield: Subfield | None = None
    field: FieldEntity | None = None
    domain: Domain | None = None

    model_config = ConfigDict(extra="allow")


class TopicShare(BaseEntity):
    """Topic share information."""

    value: float = 0.0
    subfield: Subfield | None = None
    field: FieldEntity | None = None
    domain: Domain | None = None

    model_config = ConfigDict(extra="allow")


# --- SDG ---


class SDG(BaseEntity):
    """Sustainable Development Goal."""

    score: float = 0.0

    model_config = ConfigDict(extra="allow")


# --- Keyword (dehydrated) ---


class DehydratedKeyword(BaseEntity):
    """Keyword with score, embedded in works."""

    score: float = 0.0

    model_config = ConfigDict(extra="allow")


# --- Citation metrics ---


class CitationNormalizedPercentile(BaseModel):
    """Citation normalized percentile."""

    value: float = 0.0
    is_in_top_1_percent: bool = False
    is_in_top_10_percent: bool = False

    model_config = ConfigDict(extra="allow")


class YearCountBasic(BaseModel):
    """Year-count pair for basic counts."""

    year: int | None = None
    cited_by_count: int | None = None

    model_config = ConfigDict(extra="allow")


class YearCount(BaseModel):
    """Year-count pair with works count."""

    year: int | None = None
    cited_by_count: int | None = None
    works_count: int | None = None
    oa_works_count: int | None = None

    model_config = ConfigDict(extra="allow")


class SummaryStats(BaseModel):
    """Summary statistics for an entity.

    The ``2yr_mean_citedness`` field from the API is aliased to
    ``two_yr_mean_citedness`` for Python compatibility.
    """

    two_yr_mean_citedness: float | None = Field(
        default=None, alias="2yr_mean_citedness"
    )
    h_index: int | None = None
    i10_index: int | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


# --- Institution-related ---


class Society(BaseModel):
    """Society linked to a source."""

    url: SafeStr | None = None
    organization: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class Geo(BaseModel):
    """Geographic location data."""

    city: SafeStr | None = None
    geonames_city_id: SafeStr | None = None
    region: SafeStr | None = None
    country_code: SafeStr | None = None
    country: SafeStr | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = ConfigDict(extra="allow")


class Role(BaseModel):
    """Role an organization can play."""

    role: Literal["funder", "publisher", "institution"] | None = None
    id: SafeStr = ""
    works_count: int | None = None

    model_config = ConfigDict(extra="allow")


class International(BaseModel):
    """Container for localized display labels."""

    display_name: dict[str, str] | None = None
    description: dict[str, str] | None = None

    model_config = ConfigDict(extra="allow")


class HasContent(BaseModel):
    """Content availability flags for a work."""

    pdf: bool = False
    grobid_xml: bool = False

    model_config = ConfigDict(extra="allow")


# --- Affiliation ---


class Affiliation(BaseModel):
    """Affiliation info from an authorship."""

    raw_affiliation_string: SafeStr | None = None
    institution_ids: SafeList[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


# --- Type aliases (re-exported) ---

from typing import Literal as _L  # noqa: E402

WorkType = _L[
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

SourceType = _L[
    "journal",
    "repository",
    "conference",
    "ebook platform",
    "book series",
    "metadata",
    "other",
]

InstitutionType = _L[
    "education",
    "healthcare",
    "company",
    "archive",
    "nonprofit",
    "government",
    "facility",
    "other",
    "funder",
]
