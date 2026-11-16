"""Client for the OpenAlex Awards endpoint."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..models import ApiResponse, Award
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class AwardsClient(StandardResourceClient):
    """Client for the OpenAlex Awards API endpoint."""

    _entity_path: str = "awards"
    # Widened annotations (ty 0.0.104+): a narrow override of a mutable base
    # attribute is rejected, but the value stays the per-endpoint model.
    _entity_model: type[BaseModel] | None = Award
    _search_response_model: type[BaseModel] | None = ApiResponse[Award]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
