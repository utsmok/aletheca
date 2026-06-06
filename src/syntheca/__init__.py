"""Syntheca: Python interface for the OpenAlex API."""

try:
    from importlib.metadata import PackageNotFoundError, version as _get_version

    __version__ = _get_version("syntheca")
except PackageNotFoundError:
    __version__ = "0.0.0"

from bibliofabric.exceptions import (
    APIError,
    AuthError,
    BibliofabricError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)

from .client import SynthecaClient
from .models import (
    ApiResponse,
    Author,
    Award,
    BaseEntity,
    Funder,
    Institution,
    Keyword,
    Meta,
    Publisher,
    Source,
    Topic,
    Work,
)
from .session import SynthecaSession

__all__ = [
    "__version__",
    "APIError",
    "ApiResponse",
    "AuthError",
    "Award",
    "Author",
    "BaseEntity",
    "BibliofabricError",
    "ConfigurationError",
    "Funder",
    "Institution",
    "Keyword",
    "Meta",
    "NetworkError",
    "NotFoundError",
    "Publisher",
    "RateLimitError",
    "Source",
    "SynthecaClient",
    "SynthecaSession",
    "TimeoutError",
    "Topic",
    "ValidationError",
    "Work",
]
