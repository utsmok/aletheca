"""Tests for Pydantic entity models."""

from pydantic import BaseModel, Field

from syntheca.models import ApiResponse, Author, Meta, Work
from syntheca.models.common import SummaryStats
from syntheca.models.safe_types import SafeList, SafeStr


def test_work_from_dict(sample_work_json):
    work = Work.model_validate(sample_work_json)
    assert work.title == "A Test Paper"
    assert work.publication_year == 2024
    assert work.type == "article"
    assert work.cited_by_count == 42


def test_work_extra_fields_allowed():
    data = {"id": "W1", "display_name": "Test", "unknown_field": "value"}
    work = Work.model_validate(data)
    assert work.id == "W1"


def test_meta_from_dict():
    data = {"count": 42, "next_cursor": "abc"}
    meta = Meta.model_validate(data)
    assert meta.count == 42
    assert meta.next_cursor == "abc"


def test_api_response_generic():
    data = {
        "meta": {"count": 1},
        "results": [{"id": "W1", "display_name": "Test"}],
    }
    response = ApiResponse[Work].model_validate(data)
    assert len(response.results) == 1
    assert isinstance(response.results[0], Work)


def test_safe_str_coerces_none():
    class M(BaseModel):
        name: SafeStr = ""

    m = M.model_validate({"name": None})
    assert m.name == ""


def test_safe_list_coerces_none():
    class M(BaseModel):
        items: SafeList[str] = Field(default_factory=list)

    m = M.model_validate({"items": None})
    assert m.items == []


def test_safe_list_strips_none_elements():
    class M(BaseModel):
        items: SafeList[str] = Field(default_factory=list)

    m = M.model_validate({"items": ["a", None, "b"]})
    assert m.items == ["a", "b"]


def test_author_from_minimal():
    author = Author.model_validate({"id": "A123", "display_name": "Test Author"})
    assert author.id == "A123"
    assert author.affiliations == []


def test_summary_stats_alias():
    stats = SummaryStats.model_validate({"2yr_mean_citedness": 1.5, "h_index": 10, "i10_index": 20})
    assert stats.two_yr_mean_citedness == 1.5
    assert stats.h_index == 10
    assert stats.h_index == 10
