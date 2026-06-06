"""Pydantic models for the Topic entity and hierarchy."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import Domain, FieldEntity, Subfield, TopicMinimal
from .ids import TopicIds
from .safe_types import SafeList, SafeStr


class Topic(BaseEntity):
    """An OpenAlex Topic entity."""

    description: SafeStr | None = None
    ids: TopicIds | None = None
    keywords: SafeList[str] = Field(default_factory=list)
    subfield: Subfield | None = None
    field: FieldEntity | None = None
    domain: Domain | None = None
    siblings: SafeList[TopicMinimal] = Field(default_factory=list)
    works_count: int | None = None
    cited_by_count: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None

    model_config = ConfigDict(extra="allow")
