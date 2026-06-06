"""Client for the OpenAlex Awards endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Award
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class AwardsClient(StandardResourceClient):
    """Client for the OpenAlex Awards API endpoint."""

    _entity_path: str = "awards"
    _entity_model: type[Award] = Award
    _search_response_model: type = ApiResponse[Award]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
