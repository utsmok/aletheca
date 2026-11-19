"""Fetch a work, count a query, and grab one page of results.

Run: uv run examples/quickstart.py
"""

import asyncio

from aletheca import AlethecaClient


async def main() -> None:
    async with AlethecaClient() as client:
        work = await client.works.get("W2741809807")
        print(work.title, f"({work.publication_year})")

        total = await client.works.count({"is_oa": True, "publication_year": 2024})
        print(f"OA works from 2024: {total}")

        page = await client.works.search(
            {"publication_year": 2024},
            query="photosynthesis",
            select=["id", "title"],
            page_size=5,
        )
        for result in page.results:
            print(result.id, result.title)


if __name__ == "__main__":
    asyncio.run(main())
