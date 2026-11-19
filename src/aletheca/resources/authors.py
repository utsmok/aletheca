"""Client for the OpenAlex authors endpoint."""

from collections.abc import Sequence

from ..dialect import OpenAlexResourceClient
from ..models import Author


class AuthorsClient(OpenAlexResourceClient[Author]):
    """Client for the ``/authors`` endpoint."""

    path = "authors"
    model = Author

    async def batch_get_by_openalex_id(
        self, ids: Sequence[str], *, batch_size: int | None = None
    ) -> dict[str, Author]:
        """Fetch authors by OpenAlex id (bare ``A...`` or full URL)."""
        return await self.batch_get(ids, field="openalex", batch_size=batch_size)
