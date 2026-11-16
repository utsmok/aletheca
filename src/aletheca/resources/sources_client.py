"""Client for the OpenAlex Sources endpoint."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..models import ApiResponse, Source
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class SourcesClient(StandardResourceClient):
    """Client for the OpenAlex Sources API endpoint."""

    _entity_path: str = "sources"
    # Widened annotations (ty 0.0.104+): a narrow override of a mutable base
    # attribute is rejected, but the value stays the per-endpoint model.
    _entity_model: type[BaseModel] | None = Source
    _search_response_model: type[BaseModel] | None = ApiResponse[Source]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
        "issn": "issn",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
