"""Pydantic models for the Keyword entity."""

from pydantic.config import ConfigDict

from .base import BaseEntity


class Keyword(BaseEntity):
    """An OpenAlex Keyword entity."""

    works_count: int | None = None
    cited_by_count: int | None = None
    keywords: list[dict] | None = None

    model_config = ConfigDict(extra="allow")
