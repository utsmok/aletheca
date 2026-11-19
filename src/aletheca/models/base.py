"""Base Pydantic models for OpenAlex API entities."""

from pydantic import BaseModel, ConfigDict


class BaseEntity(BaseModel):
    """Base model for all OpenAlex entities.

    All OpenAlex entities share `id` and `display_name` fields.
    Most also have `works_count` and `cited_by_count`.
    """

    id: str | None = None
    display_name: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)
