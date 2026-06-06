"""Reusable Pydantic annotated types that make API data safe to traverse.

- ``SafeList[T]`` — coerces ``None`` → ``[]``, filters null elements
- ``SafeStr`` — coerces ``None`` → ``""``
"""

from typing import Annotated, TypeVar

from pydantic import BeforeValidator

T = TypeVar("T")

SafeList = Annotated[
    list[T],
    BeforeValidator(lambda v: [] if v is None else [x for x in v if x is not None]),
]
"""List fields that coerce ``None`` → ``[]`` and strip null entries."""

SafeStr = Annotated[str, BeforeValidator(lambda v: "" if v is None else v)]
"""String fields that coerce ``None`` → ``""``."""
