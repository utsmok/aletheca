"""SynthecaResourceClient — base class for all OpenAlex resource clients.

Overrides bibliofabric's parameter names and filter serialization
for OpenAlex-specific conventions:
- ``per_page`` instead of ``pageSize``
- ``sort`` instead of ``sortBy``
- ``filter=key:value,key:value`` instead of individual query params
"""

from typing import Any

from bibliofabric.exceptions import BibliofabricError
from bibliofabric.log_config import logger
from bibliofabric.resources import (
    BaseResourceClient,
    CursorIterableMixin,
    GettableMixin,
    SearchableMixin,
)
from pydantic import BaseModel


class SynthecaResourceClient(BaseResourceClient):
    """Base for all OpenAlex resource clients.

    Sets OpenAlex-specific parameter names and overrides filter
    serialization to produce the ``filter=key:value,key:value``
    query string format.
    """

    _param_page_size: str = "per_page"
    _param_sort: str = "sort"

    def _serialize_filters(
        self, filters: BaseModel | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Serialize filters into OpenAlex's single ``filter`` query parameter.

        OpenAlex syntax::

            filter=publication_year:2024,is_oa:true
            filter=authorships.author.id:A123|A456

        Returns a dict with a single ``filter`` key containing the
        comma-joined filter string.
        """
        if filters is None:
            return {}

        if isinstance(filters, BaseModel):
            filter_dict = filters.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(filters, dict):
            filter_dict = dict(filters)
        else:
            raise BibliofabricError(
                f"filters must be a Pydantic model or dictionary, got {type(filters)}"
            )

        if not filter_dict:
            return {}

        parts = []
        for key, value in filter_dict.items():
            parts.append(f"{key}:{value}")

        return {"filter": ",".join(parts)}


class StandardResourceClient(
    GettableMixin, SearchableMixin, CursorIterableMixin, SynthecaResourceClient
):
    """Base for standard CRUD resource clients that only differ in class attributes.

    Subclasses must set:
        _entity_path (str): The API path for the resource.
        _entity_model: Pydantic model for a single entity.
        _search_response_model: Pydantic model for the search response envelope.
    """

    def __init__(self, api_client):  # noqa: ANN001
        super().__init__(api_client)
        logger.debug(
            f"{type(self).__name__} initialized for path: {self._entity_path}"
        )
