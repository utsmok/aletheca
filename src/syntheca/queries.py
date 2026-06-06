"""Convenience query functions for common OpenAlex workflows.

These functions accept a SynthecaSession as their first argument
and compose multiple API calls into higher-level operations.

Access via ``session.queries.function_name(...)``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import Work

if TYPE_CHECKING:
    from .session import SynthecaSession


async def works_by_author(
    session: SynthecaSession,
    author_name: str,
    *,
    limit: int | None = None,
) -> list[Work]:
    """Get works by an author (searches by name, then fetches their works).

    Args:
        session: Active SynthecaSession.
        author_name: Author display name to search for.
        limit: Max number of works to return.

    Returns:
        List of Work entities.
    """
    from .endpoints import AuthorsFilters

    response = await session.authors.search(
        search=author_name, page_size=1, filters=AuthorsFilters()
    )
    if isinstance(response, dict):
        results = response.get("results", [])
    else:
        results = response.results

    if not results:
        return []

    author_id = results[0].id if hasattr(results[0], "id") else results[0].get("id")
    if not author_id:
        return []

    return await session.works.collect(
        filters={"authorships.author.id": author_id},
        limit=limit,
    )


async def works_by_institution(
    session: SynthecaSession,
    institution_name: str,
    *,
    limit: int | None = None,
) -> list[Work]:
    """Get works affiliated with an institution.

    Args:
        session: Active SynthecaSession.
        institution_name: Institution display name to search for.
        limit: Max number of works to return.

    Returns:
        List of Work entities.
    """
    from .endpoints import InstitutionsFilters

    response = await session.institutions.search(
        search=institution_name, page_size=1, filters=InstitutionsFilters()
    )
    if isinstance(response, dict):
        results = response.get("results", [])
    else:
        results = response.results

    if not results:
        return []

    inst_id = results[0].id if hasattr(results[0], "id") else results[0].get("id")
    if not inst_id:
        return []

    return await session.works.collect(
        filters={"authorships.institutions.id": inst_id},
        limit=limit,
    )


async def works_by_doi(
    session: SynthecaSession,
    dois: list[str],
) -> list[Work]:
    """Fetch works by their DOIs.

    Args:
        session: Active SynthecaSession.
        dois: List of DOI strings (with or without ``https://doi.org/`` prefix).

    Returns:
        List of Work entities.
    """
    if not dois:
        return []

    # OpenAlex supports pipe-separated DOIs in the filter
    pipe_dois = "|".join(doi.strip() for doi in dois if doi.strip())
    if not pipe_dois:
        return []

    return await session.works.collect(
        filters={"doi": pipe_dois},
        limit=len(dois),
    )


async def citing_works(
    session: SynthecaSession,
    work_id: str,
    *,
    limit: int | None = None,
) -> list[Work]:
    """Get works that cite a given work.

    Args:
        session: Active SynthecaSession.
        work_id: OpenAlex work ID (e.g., ``W1234567890``).
        limit: Max number of works to return.

    Returns:
        List of citing Work entities.
    """
    return await session.works.collect(
        filters={"cites": work_id},
        limit=limit,
    )


async def referenced_works(
    session: SynthecaSession,
    work_id: str,
    *,
    limit: int | None = None,
) -> list[Work]:
    """Get works referenced by a given work.

    Args:
        session: Active SynthecaSession.
        work_id: OpenAlex work ID (e.g., ``W1234567890``).
        limit: Max number of works to return.

    Returns:
        List of referenced Work entities.
    """
    return await session.works.collect(
        filters={"cited_by": work_id},
        limit=limit,
    )
