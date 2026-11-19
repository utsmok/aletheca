"""Resource clients for the OpenAlex entity endpoints."""

from .authors import AuthorsClient
from .awards import AwardsClient
from .funders import FundersClient
from .institutions import InstitutionsClient
from .keywords import KeywordsClient
from .links import LinksClient
from .locations import LocationsClient
from .publishers import PublishersClient
from .sources import SourcesClient
from .topics import TopicsClient
from .works import WorksClient

__all__ = [
    "AuthorsClient",
    "AwardsClient",
    "FundersClient",
    "InstitutionsClient",
    "KeywordsClient",
    "LinksClient",
    "LocationsClient",
    "PublishersClient",
    "SourcesClient",
    "TopicsClient",
    "WorksClient",
]
