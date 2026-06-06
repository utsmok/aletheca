"""Client for the OpenAlex Topics endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Topic
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class TopicsClient(StandardResourceClient):
    """Client for the OpenAlex Topics API endpoint."""

    _entity_path: str = "topics"
    _entity_model: type[Topic] = Topic
    _search_response_model: type = ApiResponse[Topic]
    _supports_direct_get: bool = True

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
