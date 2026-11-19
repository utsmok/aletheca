"""Aletheca: Python interface for the OpenAlex API."""

try:
    from importlib.metadata import PackageNotFoundError, version as _get_version

    __version__ = _get_version("aletheca")
except PackageNotFoundError:
    __version__ = "0.0.0"

from bibliofabric import Page
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

from .client import AlethecaClient
from .config import AlethecaSettings
from .filters import (
    AuthorsFilters,
    AwardsFilters,
    FundersFilters,
    InstitutionsFilters,
    KeywordsFilters,
    PublishersFilters,
    SourcesFilters,
    TopicsFilters,
    WorksFilters,
)
from .models import (
    Author,
    AutocompleteResult,
    Award,
    BaseEntity,
    Funder,
    GroupByBucket,
    Institution,
    Keyword,
    Publisher,
    RateLimitStatus,
    Source,
    Topic,
    Work,
)

__all__ = [
    "__version__",
    "APIError",
    "AuthError",
    "Author",
    "AuthorsFilters",
    "AutocompleteResult",
    "Award",
    "AwardsFilters",
    "AlethecaClient",
    "AlethecaSettings",
    "BaseEntity",
    "BibliofabricError",
    "ConfigurationError",
    "Funder",
    "FundersFilters",
    "GroupByBucket",
    "Institution",
    "InstitutionsFilters",
    "Keyword",
    "KeywordsFilters",
    "NetworkError",
    "NotFoundError",
    "Page",
    "Publisher",
    "PublishersFilters",
    "RateLimitError",
    "RateLimitStatus",
    "Source",
    "SourcesFilters",
    "TimeoutError",
    "Topic",
    "TopicsFilters",
    "ValidationError",
    "Work",
    "WorksFilters",
]
