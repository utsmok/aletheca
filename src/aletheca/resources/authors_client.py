"""Client for the OpenAlex Authors endpoint."""

from typing import TYPE_CHECKING

from ..models import ApiResponse, Author
from ..resources._standard import StandardResourceClient

if TYPE_CHECKING:
    from ..client import AlethecaClient


class AuthorsClient(StandardResourceClient):
    """Client for the OpenAlex Authors API endpoint."""

    _entity_path: str = "authors"
    _entity_model: type[Author] = Author
    _search_response_model: type = ApiResponse[Author]
    _supports_direct_get: bool = True
    _batch_fields: dict[str, str] = {
        "openalex_id": "openalex",
        "orcid": "orcid",
        "scopus_id": "scopus",
    }

    def __init__(self, api_client: "AlethecaClient"):
        super().__init__(api_client)
