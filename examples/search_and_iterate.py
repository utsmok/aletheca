"""Filter models, scoped search, and cursor iteration.

Run: uv run examples/search_and_iterate.py  (a key is needed for iterate)
"""

import asyncio

from aletheca import AlethecaClient, WorksFilters


async def main() -> None:
    async with AlethecaClient() as client:
        # Typed filters serialize to filter=publication_year:2024,is_oa:true.
        filters = WorksFilters(publication_year=2024, is_oa=True)
        page = await client.works.search(
            filters,
            sort="cited_by_count:desc",
            select=["id", "title", "cited_by_count"],
        )
        for work in page.results[:3]:
            print(work.cited_by_count, work.title)

        # Scoped searches use the search.* parameters.
        titles = await client.works.search_scoped(
            "CRISPR", scope="title_and_abstract", page_size=3
        )
        for work in titles.results:
            print("title hit:", work.title)

        # Cursor iteration over every match, 100 per page.
        ids = [
            work.id
            async for work in client.works.iterate(filters, select=["id"], limit=200)
        ]
        print(f"collected {len(ids)} ids")


if __name__ == "__main__":
    asyncio.run(main())
