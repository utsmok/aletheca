"""Resource clients for OpenAlex API endpoints."""

from .authors_client import AuthorsClient
from .funders_client import FundersClient
from .institutions_client import InstitutionsClient
from .keywords_client import KeywordsClient
from .publishers_client import PublishersClient
from .sources_client import SourcesClient
from .topics_client import TopicsClient
from .works_client import WorksClient

__all__ = [
    "AuthorsClient",
    "FundersClient",
    "InstitutionsClient",
    "KeywordsClient",
    "PublishersClient",
    "SourcesClient",
    "TopicsClient",
    "WorksClient",
]
