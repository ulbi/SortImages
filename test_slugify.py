import pytest
from sortinfolder import slugify


class TestSlugify:
    """Tests for the slugify helper function."""

    def test_basic_ascii_text(self):
        """Test basic ASCII text conversion to slug."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test Case") == "test-case"
        assert slugify("Multiple   Spaces") == "multiple-spaces"

    def test_german_umlauts(self):
        """Test German umlaut transliteration."""
        assert slugify("Müller") == "mueller"
        assert slugify("Größe") == "groesse"
        assert slugify("Füße") == "fuesse"
        assert slugify("Äpfel") == "aepfel"
        assert slugify("Öl") == "oel"
        assert slugify("Über") == "ueber"

    def test_sharp_s(self):
        """Test German sharp S (ß) transliteration."""
        assert slugify("Straße") == "strasse"
        assert slugify("Weiß") == "weiss"

    def test_mixed_umlauts_and_ascii(self):
        """Test mixed umlauts and ASCII characters."""
        assert slugify("Müller & Söhne") == "mueller-soehne"
        assert slugify("Größe: 100%") == "groesse-100"

    def test_special_characters_removed(self):
        """Test that special characters are removed/replaced."""
        assert slugify("Hello@World!") == "hello-world"
        assert slugify("Test#$%^&*()") == "test"
        assert slugify("Path/To/File") == "path-to-file"

    def test_numbers_preserved(self):
        """Test that numbers are preserved."""
        assert slugify("Version 2.0") == "version-2-0"
        assert slugify("Year 2024") == "year-2024"

    def test_leading_trailing_hyphens_stripped(self):
        """Test that leading and trailing hyphens are stripped."""
        assert slugify("  Hello World  ") == "hello-world"
        assert slugify("---Test---") == "test"
        assert slugify("---") == ""

    def test_empty_string(self):
        """Test empty string returns empty string."""
        assert slugify("") == ""

    def test_only_special_chars(self):
        """Test string with only special characters."""
        assert slugify("@#$%") == ""

    def test_unicode_normalization(self):
        """Test unicode normalization for accented characters."""
        assert slugify("café") == "cafe"
        assert slugify("naïve") == "naive"
        assert slugify("résumé") == "resume"