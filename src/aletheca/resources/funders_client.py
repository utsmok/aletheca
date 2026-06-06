"""Client for the OpenAlex Funders endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Funder
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class FundersClient(StandardResourceClient):
    """Client for the OpenAlex Funders API endpoint."""

    _entity_path: str = "funders"
    _entity_model: type[Funder] = Funder
    _search_response_model: type = ApiResponse[Funder]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
