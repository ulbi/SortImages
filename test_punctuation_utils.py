import pytest
from punctuation_utils import remove_punctuation, count_punctuation, ends_with_punctuation


class TestRemovePunctuation:
    def test_remove_punctuation_basic(self):
        assert remove_punctuation("Hello, world!") == "Hello world"

    def test_remove_punctuation_multiple(self):
        assert remove_punctuation("Hello... world???") == "Hello world"

    def test_remove_punctuation_none(self):
        assert remove_punctuation("Hello world") == "Hello world"

    def test_remove_punctuation_empty(self):
        assert remove_punctuation("") == ""

    def test_remove_punctuation_only_punctuation(self):
        assert remove_punctuation("!@#$%^&*()") == ""


class TestCountPunctuation:
    def test_count_punctuation_basic(self):
        assert count_punctuation("Hello, world!") == 2

    def test_count_punctuation_multiple(self):
        assert count_punctuation("Hello... world???") == 6

    def test_count_punctuation_none(self):
        assert count_punctuation("Hello world") == 0

    def test_count_punctuation_empty(self):
        assert count_punctuation("") == 0


class TestEndsWithPunctuation:
    def test_ends_with_punctuation_true(self):
        assert ends_with_punctuation("Hello!") is True
        assert ends_with_punctuation("Hello?") is True
        assert ends_with_punctuation("Hello.") is True

    def test_ends_with_punctuation_false(self):
        assert ends_with_punctuation("Hello") is False
        assert ends_with_punctuation("Hello world") is False

    def test_ends_with_punctuation_empty(self):
        assert ends_with_punctuation("") is False