"""Client for the OpenAlex Publishers endpoint."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..models import ApiResponse, Publisher
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class PublishersClient(StandardResourceClient):
    """Client for the OpenAlex Publishers API endpoint."""

    _entity_path: str = "publishers"
    # Widened annotations (ty 0.0.104+): a narrow override of a mutable base
    # attribute is rejected, but the value stays the per-endpoint model.
    _entity_model: type[BaseModel] | None = Publisher
    _search_response_model: type[BaseModel] | None = ApiResponse[Publisher]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
        "ror": "ror",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
