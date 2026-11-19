"""Pydantic models for the Keyword entity."""

from bibliofabric import SafeList, SafeStr
from pydantic import Field
from pydantic.config import ConfigDict

from .base import BaseEntity
from .common import DehydratedTopic
from .ids import KeywordIds


class Keyword(BaseEntity):
    """An OpenAlex Keyword entity."""

    description: SafeStr | None = None
    display_name_alternatives: SafeList[str] = Field(default_factory=list)
    ids: KeywordIds | None = None
    primary_topic: DehydratedTopic | None = None
    topics: SafeList[DehydratedTopic] = Field(default_factory=list)
    works_count: int | None = None
    cited_by_count: int | None = None
    # Common fields
    created_date: str | None = None
    updated_date: str | None = None
    works_api_url: str | None = None

    model_config = ConfigDict(extra="allow")
