"""Client for the OpenAlex Keywords endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Keyword
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import SynthecaClient


class KeywordsClient(StandardResourceClient):
    """Client for the OpenAlex Keywords API endpoint."""

    _entity_path: str = "keywords"
    _entity_model: type[Keyword] = Keyword
    _search_response_model: type = ApiResponse[Keyword]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "SynthecaClient"):
        super().__init__(api_client)
