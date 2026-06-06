"""Client for the OpenAlex Sources endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Source
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class SourcesClient(StandardResourceClient):
    """Client for the OpenAlex Sources API endpoint."""

    _entity_path: str = "sources"
    _entity_model: type[Source] = Source
    _search_response_model: type = ApiResponse[Source]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
