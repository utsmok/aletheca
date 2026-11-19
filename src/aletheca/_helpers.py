"""Helpers shared by aletheca models: abstract reconstruction."""


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
