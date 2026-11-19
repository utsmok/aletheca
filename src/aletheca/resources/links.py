"""Client for the OpenAlex links endpoint."""

from ..dialect import OpenAlexResourceClient
from ..models import Link


class LinksClient(OpenAlexResourceClient[Link]):
    """Client for the ``/links`` endpoint.

    Typed one-hop edges between works, each labeled with a relationship
    (``https://openalex.org/relationships/citation`` and part-of
    relationships). ``origin()`` lists the edges leaving a work, ``target()``
    the edges pointing at it; ``get``/``search``/``iterate`` are available
    for raw ``filter=origin:``/``target:`` queries.
    """

    path = "links"
    model = Link

    async def origin(self, work_id: str, *, limit: int = 100) -> list[Link]:
        """Collect the edges leaving ``work_id`` (what it cites or contains).

        Fetches ``filter=origin:<id>`` with cursor paging, up to ``limit``
        edges. Ids normalize (bare ``W...`` or full URL).
        """
        return await self.collect({"origin": self.normalize_id(work_id)}, limit=limit)

    async def target(self, work_id: str, *, limit: int = 100) -> list[Link]:
        """Collect the edges pointing at ``work_id`` (what cites or contains it).

        Fetches ``filter=target:<id>`` with cursor paging, up to ``limit``
        edges; heavily cited works need a small ``limit``.
        """
        return await self.collect({"target": self.normalize_id(work_id)}, limit=limit)
