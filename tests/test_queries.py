"""Tests for syntheca.queries convenience functions."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from syntheca.queries import (
    citing_works,
    referenced_works,
    works_by_author,
    works_by_doi,
    works_by_institution,
)


@pytest.fixture
def session():
    """Mock SynthecaSession with async resource clients."""
    sess = MagicMock()

    sess.works = MagicMock()
    sess.works.collect = AsyncMock(return_value=[])

    sess.authors = MagicMock()
    sess.authors.search = AsyncMock(return_value=MagicMock(results=[]))

    sess.institutions = MagicMock()
    sess.institutions.search = AsyncMock(return_value=MagicMock(results=[]))

    return sess


# ---------------------------------------------------------------------------
# works_by_author
# ---------------------------------------------------------------------------


class TestWorksByAuthor:
    @pytest.mark.asyncio
    async def test_with_name_only(self, session):
        author_result = MagicMock()
        author_result.id = "https://openalex.org/A123"
        session.authors.search.return_value = MagicMock(results=[author_result])

        await works_by_author(session, "John Doe")

        session.authors.search.assert_called_once()
        search_kwargs = session.authors.search.call_args[1]
        assert search_kwargs["search"] == "John Doe"

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {
            "authorships.author.id": "https://openalex.org/A123"
        }
        assert collect_kwargs["limit"] is None

    @pytest.mark.asyncio
    async def test_with_limit(self, session):
        author_result = MagicMock()
        author_result.id = "https://openalex.org/A456"
        session.authors.search.return_value = MagicMock(results=[author_result])

        await works_by_author(session, "Jane Smith", limit=10)

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["limit"] == 10

    @pytest.mark.asyncio
    async def test_author_not_found(self, session):
        session.authors.search.return_value = MagicMock(results=[])

        result = await works_by_author(session, "Nobody")

        assert result == []
        session.works.collect.assert_not_called()

    @pytest.mark.asyncio
    async def test_author_no_id(self, session):
        author_result = MagicMock()
        author_result.id = None
        session.authors.search.return_value = MagicMock(results=[author_result])

        result = await works_by_author(session, "NoId")

        assert result == []
        session.works.collect.assert_not_called()


# ---------------------------------------------------------------------------
# works_by_institution
# ---------------------------------------------------------------------------


class TestWorksByInstitution:
    @pytest.mark.asyncio
    async def test_with_name_only(self, session):
        inst_result = MagicMock()
        inst_result.id = "https://openalex.org/I789"
        session.institutions.search.return_value = MagicMock(results=[inst_result])

        await works_by_institution(session, "MIT")

        session.institutions.search.assert_called_once()
        search_kwargs = session.institutions.search.call_args[1]
        assert search_kwargs["search"] == "MIT"

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {
            "authorships.institutions.id": "https://openalex.org/I789"
        }
        assert collect_kwargs["limit"] is None

    @pytest.mark.asyncio
    async def test_with_limit(self, session):
        inst_result = MagicMock()
        inst_result.id = "https://openalex.org/I999"
        session.institutions.search.return_value = MagicMock(results=[inst_result])

        await works_by_institution(session, "Stanford", limit=5)

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["limit"] == 5

    @pytest.mark.asyncio
    async def test_institution_not_found(self, session):
        session.institutions.search.return_value = MagicMock(results=[])

        result = await works_by_institution(session, "Unknown")

        assert result == []
        session.works.collect.assert_not_called()


# ---------------------------------------------------------------------------
# works_by_doi
# ---------------------------------------------------------------------------


class TestWorksByDoi:
    @pytest.mark.asyncio
    async def test_single_doi(self, session):
        await works_by_doi(session, ["10.1234/test"])

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"doi": "10.1234/test"}
        assert collect_kwargs["limit"] == 1

    @pytest.mark.asyncio
    async def test_multiple_dois(self, session):
        await works_by_doi(session, ["10.1/a", "10.2/b", "10.3/c"])

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"doi": "10.1/a|10.2/b|10.3/c"}
        assert collect_kwargs["limit"] == 3

    @pytest.mark.asyncio
    async def test_empty_list(self, session):
        result = await works_by_doi(session, [])

        assert result == []
        session.works.collect.assert_not_called()

    @pytest.mark.asyncio
    async def test_strips_whitespace(self, session):
        await works_by_doi(session, [" 10.1/a ", " 10.2/b "])

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"doi": "10.1/a|10.2/b"}

    @pytest.mark.asyncio
    async def test_filters_empty_strings(self, session):
        await works_by_doi(session, ["", "  ", "10.1/a"])

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"doi": "10.1/a"}


# ---------------------------------------------------------------------------
# citing_works
# ---------------------------------------------------------------------------


class TestCitingWorks:
    @pytest.mark.asyncio
    async def test_basic(self, session):
        await citing_works(session, "W1234567890")

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"cites": "W1234567890"}
        assert collect_kwargs["limit"] is None

    @pytest.mark.asyncio
    async def test_with_limit(self, session):
        await citing_works(session, "W1234567890", limit=10)

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["limit"] == 10


# ---------------------------------------------------------------------------
# referenced_works
# ---------------------------------------------------------------------------


class TestReferencedWorks:
    @pytest.mark.asyncio
    async def test_basic(self, session):
        await referenced_works(session, "W1234567890")

        session.works.collect.assert_called_once()
        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["filters"] == {"cited_by": "W1234567890"}
        assert collect_kwargs["limit"] is None

    @pytest.mark.asyncio
    async def test_with_limit(self, session):
        await referenced_works(session, "W1234567890", limit=25)

        collect_kwargs = session.works.collect.call_args[1]
        assert collect_kwargs["limit"] == 25
