"""Pydantic models for the Institution entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import (
    Geo,
    International,
    Role,
    TopicCount,
    TopicShare,
    YearCount,
)
from .dehydrated import RelatedInstitution
from .ids import InstitutionIds
from .safe_types import SafeList, SafeStr


class Repository(BaseEntity):
    """Repository linked to an institution."""

    host_organization: SafeStr | None = None
    host_organization_lineage: SafeList[str] = Field(default_factory=list)
    host_organization_name: SafeStr | None = None

    model_config = ConfigDict(extra="allow")


class Institution(BaseEntity):
    """An OpenAlex Institution entity."""

    ids: InstitutionIds | None = None
    is_super_system: bool | None = None
    type: str | None = None

    associated_institutions: SafeList[RelatedInstitution] = Field(
        default_factory=list
    )
    country_code: SafeStr | None = None
    counts_by_year: SafeList[YearCount] = Field(default_factory=list)
    display_name_acronyms: SafeList[str] = Field(default_factory=list)
    display_name_alternatives: SafeList[str] = Field(default_factory=list)
    geo: Geo | None = None
    homepage_url: SafeStr | None = None
    image_thumbnail_url: SafeStr | None = None
    image_url: SafeStr | None = None
    international: International | None = None
    lineage: SafeList[str] = Field(default_factory=list)
    repositories: SafeList[Repository] = Field(default_factory=list)
    roles: SafeList[Role] = Field(default_factory=list)
    ror: SafeStr | None = None
    works_count: int | None = None
    cited_by_count: int | None = None

    # Deprecated
    x_concepts: SafeList[dict] = Field(default_factory=list)

    # Topics
    topics: SafeList[TopicCount] = Field(default_factory=list)
    topic_share: SafeList[TopicShare] = Field(default_factory=list)

    # Undocumented
    type_id: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
