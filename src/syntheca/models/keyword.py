"""Pydantic models for the Keyword entity."""

from pydantic.config import ConfigDict

from .base import BaseEntity


class Keyword(BaseEntity):
    """An OpenAlex Keyword entity."""

    works_count: int | None = None
    cited_by_count: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None

    model_config = ConfigDict(extra="allow")
