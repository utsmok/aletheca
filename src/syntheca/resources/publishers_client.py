"""Client for the OpenAlex Publishers endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Publisher
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import SynthecaClient


class PublishersClient(StandardResourceClient):
    """Client for the OpenAlex Publishers API endpoint."""

    _entity_path: str = "publishers"
    _entity_model: type[Publisher] = Publisher
    _search_response_model: type = ApiResponse[Publisher]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "SynthecaClient"):
        super().__init__(api_client)
