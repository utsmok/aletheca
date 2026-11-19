# tests/test_str_repr.py
"""Tests for __str__ and __repr__ on entity models."""

from aletheca.models import (
    Author,
    Funder,
    Institution,
    Publisher,
    Source,
    Topic,
    Work,
)


class TestWorkStr:
    def test_full_str(self):
        w = Work.model_validate(
            {
                "id": "https://openalex.org/W123",
                "display_name": "A Study of Something Important",
            }
        )
        s = str(w)
        assert "A Study of Something Important" in s
        assert "W123" in s

    def test_minimal_str(self):
        w = Work.model_validate({"id": "https://openalex.org/W999"})
        r = repr(w)
        assert "Work" in r
        assert "W999" in r


class TestAuthorStr:
    def test_with_display_name(self):
        a = Author.model_validate(
            {
                "id": "https://openalex.org/A456",
                "display_name": "Jane Doe",
            }
        )
        s = str(a)
        assert "Jane Doe" in s
        assert "A456" in s

    def test_fallback_to_id(self):
        a = Author.model_validate({"id": "https://openalex.org/A000"})
        r = repr(a)
        assert "Author" in r
        assert "A000" in r


class TestSourceStr:
    def test_with_display_name(self):
        src = Source.model_validate(
            {
                "id": "https://openalex.org/S789",
                "display_name": "Nature",
            }
        )
        s = str(src)
        assert "Nature" in s
        assert "S789" in s

    def test_fallback_to_id(self):
        src = Source.model_validate({"id": "https://openalex.org/S000"})
        r = repr(src)
        assert "Source" in r
        assert "S000" in r


class TestInstitutionStr:
    def test_with_display_name(self):
        inst = Institution.model_validate(
            {
                "id": "https://openalex.org/I123",
                "display_name": "MIT",
            }
        )
        s = str(inst)
        assert "MIT" in s
        assert "I123" in s

    def test_fallback_to_id(self):
        inst = Institution.model_validate({"id": "https://openalex.org/I000"})
        r = repr(inst)
        assert "Institution" in r
        assert "I000" in r


class TestTopicStr:
    def test_with_description(self):
        t = Topic.model_validate(
            {
                "id": "https://openalex.org/T111",
                "display_name": "Machine Learning",
                "description": "Algorithms that learn from data",
            }
        )
        s = str(t)
        assert "Machine Learning" in s
        assert "T111" in s

    def test_fallback_to_id(self):
        t = Topic.model_validate({"id": "https://openalex.org/T000"})
        r = repr(t)
        assert "Topic" in r
        assert "T000" in r


class TestPublisherStr:
    def test_with_display_name(self):
        pub = Publisher.model_validate(
            {
                "id": "https://openalex.org/P222",
                "display_name": "Elsevier",
            }
        )
        s = str(pub)
        assert "Elsevier" in s
        assert "P222" in s

    def test_fallback_to_id(self):
        pub = Publisher.model_validate({"id": "https://openalex.org/P000"})
        r = repr(pub)
        assert "Publisher" in r
        assert "P000" in r


class TestFunderStr:
    def test_with_display_name(self):
        f = Funder.model_validate(
            {
                "id": "https://openalex.org/F333",
                "display_name": "NIH",
            }
        )
        s = str(f)
        assert "NIH" in s
        assert "F333" in s

    def test_fallback_to_id(self):
        f = Funder.model_validate({"id": "https://openalex.org/F000"})
        r = repr(f)
        assert "Funder" in r
        assert "F000" in r
