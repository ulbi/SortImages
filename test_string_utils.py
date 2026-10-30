import pytest

import string_utils


def test_reverse_string_returns_reversed_text():
    assert string_utils.reverse_string("hello") == "olleh"


def test_reverse_string_handles_empty_string():
    assert string_utils.reverse_string("") == ""


def test_reverse_string_handles_single_character():
    assert string_utils.reverse_string("a") == "a"


def test_reverse_string_handles_unicode():
    assert string_utils.reverse_string("héllo wörld") == "dlröw olléh"


def test_reverse_string_handles_spaces_and_punctuation():
    assert string_utils.reverse_string("a b c!") == "!c b a"


def test_reverse_string_is_reversible():
    """Reversing twice returns the original string."""
    text = "SortImages"
    assert string_utils.reverse_string(string_utils.reverse_string(text)) == text


def test_reverse_string_raises_type_error_for_non_string():
    with pytest.raises(TypeError):
        string_utils.reverse_string(123)