"""Batch retrieval by DOI and the citation-graph helpers.

Run: uv run examples/batch_and_citations.py
"""

import asyncio

from aletheca import AlethecaClient


async def main() -> None:
    async with AlethecaClient() as client:
        # DOIs are normalized; missing records are absent from the dict.
        works = await client.works.batch_get_by_doi(
            ["10.7717/peerj.4375", "https://doi.org/10.1038/nature12373"]
        )
        for doi, work in works.items():
            print(doi, "->", work.title)

        # Who cites this paper (up to 100)?
        seed = await client.works.get("W2741809807")
        assert seed.id is not None
        citing = await client.works.citing(seed.id, limit=10)
        print(f"{len(citing)} citing works fetched")

        # What does it reference?
        refs = await client.works.referenced(seed.id, limit=10)
        print(f"{len(refs)} referenced works fetched")

        # Budget check is free.
        status = await client.rate_limit()
        assert status.rate_limit is not None
        print(f"remaining budget: {status.rate_limit.daily_remaining_usd}")


if __name__ == "__main__":
    asyncio.run(main())
