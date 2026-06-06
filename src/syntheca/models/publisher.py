"""Pydantic models for the Publisher entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import Role, SummaryStats, YearCount
from .ids import PublisherIds
from .safe_types import SafeList, SafeStr


class Publisher(BaseEntity):
    """An OpenAlex Publisher entity."""

    hierarchy_level: int | None = None
    ids: PublisherIds | None = None
    sources_api_url: SafeStr | None = None

    alternate_titles: SafeList[str] = Field(default_factory=list)
    country_codes: SafeList[str] = Field(default_factory=list)
    counts_by_year: SafeList[YearCount] = Field(default_factory=list)
    image_thumbnail_url: SafeStr | None = None
    image_url: SafeStr | None = None
    lineage: SafeList[str] = Field(default_factory=list)
    parent_publisher: dict | None = None
    roles: SafeList[Role] = Field(default_factory=list)
    works_count: int | None = None
    cited_by_count: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None
    summary_stats: SummaryStats | None = None

    # Undocumented
    homepage_url: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
