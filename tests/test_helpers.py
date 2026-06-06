"""Tests for _helpers utility functions."""

from syntheca._helpers import (
    detect_id_type,
    normalize_doi,
    parse_openalex_id,
    reconstruct_abstract,
)


def test_normalize_doi_with_prefix():
    assert normalize_doi("https://doi.org/10.1234/x") == "10.1234/x"


def test_normalize_doi_bare():
    assert normalize_doi("10.1234/x") == "10.1234/x"


def test_normalize_doi_http():
    assert normalize_doi("http://doi.org/10.1234/x") == "10.1234/x"


def test_parse_openalex_id_url():
    assert parse_openalex_id("https://openalex.org/W1234567890") == "W1234567890"


def test_parse_openalex_id_bare():
    assert parse_openalex_id("W1234567890") == "W1234567890"


def test_detect_id_type_openalex():
    assert detect_id_type("W1234567890") == "openalex"
    assert detect_id_type("A1234567890") == "openalex"


def test_detect_id_type_doi():
    assert detect_id_type("10.1234/test") == "doi"


def test_detect_id_type_pmid():
    assert detect_id_type("12345678") == "pmid"


def test_detect_id_type_unknown():
    assert detect_id_type("unknown-thing") is None


def test_reconstruct_abstract():
    inverted = {"Hello": [0], "world": [1]}
    assert reconstruct_abstract(inverted) == "Hello world"


def test_reconstruct_abstract_none():
    assert reconstruct_abstract(None) is None


def test_reconstruct_abstract_empty():
    assert reconstruct_abstract({}) is None
