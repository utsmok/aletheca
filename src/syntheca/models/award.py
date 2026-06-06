"""Pydantic models for the Award entity."""

from pydantic.config import ConfigDict

from .base import BaseEntity
from .safe_types import SafeStr


class Award(BaseEntity):
    """An OpenAlex Award entity."""

    ids: dict | None = None
    funder: SafeStr | None = None
    funder_display_name: SafeStr | None = None
    award_id: SafeStr | None = None

    model_config = ConfigDict(extra="allow")
