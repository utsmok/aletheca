"""Utility helpers for working with OpenAlex identifiers and data."""

from __future__ import annotations

import re


def normalize_doi(doi: str) -> str:
    """Normalize a DOI to its bare form (no URL prefix).

    Args:
        doi: A DOI string, possibly with ``https://doi.org/`` prefix.

    Returns:
        The bare DOI string.

    Examples:
        >>> normalize_doi("https://doi.org/10.1234/x")
        "10.1234/x"
        >>> normalize_doi("10.1234/x")
        "10.1234/x"
    """
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/"):
        if doi.startswith(prefix):
            return doi[len(prefix) :]
    return doi


def parse_openalex_id(url_or_id: str) -> str:
    """Extract the short OpenAlex ID from a full URL or bare ID.

    Args:
        url_or_id: An OpenAlex ID or URL (e.g., ``https://openalex.org/W123``).

    Returns:
        The short ID (e.g., ``W123``).

    Examples:
        >>> parse_openalex_id("https://openalex.org/W1234567890")
        "W1234567890"
        >>> parse_openalex_id("W1234567890")
        "W1234567890"
    """
    url_or_id = url_or_id.strip()
    match = re.search(r"([WAITSFPDC]\d+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id


def detect_id_type(identifier: str) -> str | None:
    """Detect the type of a scholarly identifier.

    Args:
        identifier: A string identifier.

    Returns:
        One of ``"openalex"``, ``"doi"``, ``"pmid"``, ``"orcid"``,
        ``"issn"``, ``"ror"``, or ``None``.
    """
    identifier = identifier.strip().lower()

    if re.match(r"^[WAITSFPDC]\d+$", identifier):
        return "openalex"
    if identifier.startswith("10.") or "doi.org/" in identifier:
        return "doi"
    if re.match(r"^\d{4}-\d{3,4}$", identifier):
        return "issn"
    if re.match(r"^\d{7,8}$", identifier):
        return "pmid"
    if identifier.startswith("https://orcid.org/") or re.match(
        r"\d{4}-\d{4}-\d{4}-\d{4}", identifier
    ):
        return "orcid"
    if identifier.startswith("https://ror.org/") or re.match(
        r"^0[a-hj-km-np-tv-z]{2,3}\w{3,14}$", identifier
    ):
        return "ror"
    return None


def reconstruct_abstract(
    inverted_index: dict[str, list[int]] | None,
) -> str | None:
    """Reconstruct an abstract from OpenAlex's inverted index format.

    Args:
        inverted_index: Mapping of word → list of positions.

    Returns:
        The reconstructed abstract string, or None if input is None/empty.
    """
    if not inverted_index:
        return None

    words: dict[int, str] = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word

    if not words:
        return None

    return " ".join(words[i] for i in sorted(words.keys()))
