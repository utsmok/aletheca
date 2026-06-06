"""Pydantic models for the Funder entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import Role, YearCount
from .ids import FunderIds
from .safe_types import SafeList, SafeStr


class Funder(BaseEntity):
    """An OpenAlex Funder entity."""

    ids: FunderIds | None = None
    grants_count: int | None = None

    alternate_titles: SafeList[str] = Field(default_factory=list)
    country_code: SafeStr | None = None
    counts_by_year: SafeList[YearCount] = Field(default_factory=list)
    description: SafeStr | None = None
    homepage_url: SafeStr | None = None
    image_thumbnail_url: SafeStr | None = None
    image_url: SafeStr | None = None
    roles: SafeList[Role] = Field(default_factory=list)
    works_count: int | None = None
    cited_by_count: int | None = None

    model_config = ConfigDict(extra="allow")
