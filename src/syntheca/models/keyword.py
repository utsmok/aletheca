"""Pydantic models for the Keyword entity."""

from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .safe_types import SafeStr


class Keyword(BaseEntity):
    """An OpenAlex Keyword entity."""

    works_count: int | None = None
    cited_by_count: int | None = None
    keywords: list[dict] | None = None

    model_config = ConfigDict(extra="allow")
