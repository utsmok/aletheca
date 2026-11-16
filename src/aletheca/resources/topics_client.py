"""Client for the OpenAlex Topics endpoint."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..models import ApiResponse, Topic
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class TopicsClient(StandardResourceClient):
    """Client for the OpenAlex Topics API endpoint."""

    _entity_path: str = "topics"
    # Widened annotations (ty 0.0.104+): a narrow override of a mutable base
    # attribute is rejected, but the value stays the per-endpoint model.
    _entity_model: type[BaseModel] | None = Topic
    _search_response_model: type[BaseModel] | None = ApiResponse[Topic]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
