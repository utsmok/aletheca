"""Client for the OpenAlex Institutions endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Institution
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class InstitutionsClient(StandardResourceClient):
    """Client for the OpenAlex Institutions API endpoint."""

    _entity_path: str = "institutions"
    _entity_model: type[Institution] = Institution
    _search_response_model: type = ApiResponse[Institution]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
        "ror": "ror",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
