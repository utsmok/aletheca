"""Base Pydantic models for OpenAlex API entities and responses."""

from typing import TypeVar

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

EntityType = TypeVar("EntityType", bound="BaseEntity")


class Meta(BaseModel):
    """OpenAlex response metadata envelope."""

    count: int | None = None
    db_response_time_ms: float | None = None
    page: int | None = None
    per_page: int | None = None
    next_cursor: str | None = None
    groups_count: int | None = None
    cost_usd: float | None = None

    model_config = ConfigDict(extra="allow")


class BaseEntity(BaseModel):
    """Base model for all OpenAlex entities.

    All OpenAlex entities share `id` and `display_name` fields.
    Most also have `works_count` and `cited_by_count`.
    """

    id: str | None = None
    display_name: str | None = None

    model_config = ConfigDict(extra="allow")


class ApiResponse[EntityType: "BaseEntity"](BaseModel):
    """Generic envelope for OpenAlex list/search responses."""

    meta: Meta = Field(default_factory=Meta)
    results: list[EntityType] = Field(default_factory=list)
    group_by: list[dict] | None = None

    model_config = ConfigDict(extra="allow")
