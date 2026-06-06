"""Tests for OpenAlexUnwrapper."""


def test_unwrap_results(unwrapper):
    data = {"meta": {"count": 2}, "results": [{"id": "1"}, {"id": "2"}]}
    assert unwrapper.unwrap_results(data) == [{"id": "1"}, {"id": "2"}]


def test_unwrap_results_missing_key(unwrapper):
    assert unwrapper.unwrap_results({}) == []


def test_unwrap_single_item(unwrapper):
    data = {"id": "W123", "title": "Test"}
    assert unwrapper.unwrap_single_item(data) == data


def test_get_next_page_token(unwrapper):
    data = {"meta": {"next_cursor": "abc123"}}
    assert unwrapper.get_next_page_token(data) == "abc123"


def test_get_next_page_token_none(unwrapper):
    assert unwrapper.get_next_page_token({}) is None
    assert unwrapper.get_next_page_token({"meta": {}}) is None


def test_get_total_results(unwrapper):
    data = {"meta": {"count": 42}}
    assert unwrapper.get_total_results(data) == 42


def test_get_total_results_none(unwrapper):
    assert unwrapper.get_total_results({}) is None
    assert unwrapper.get_total_results({"meta": {}}) is None


def test_get_total_results_string(unwrapper):
    data = {"meta": {"count": "42"}}
    assert unwrapper.get_total_results(data) == 42
