import subprocess
import sys

import pytest

from sortinfolder import trim_sort_folder_name


def test_help_shows_usage_and_examples():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    assert "usage: sortimages" in output
    assert "options:" in output
    assert "Examples:" in output


def test_trim_strips_surrounding_spaces():
    """Spaces on both sides are removed."""
    assert trim_sort_folder_name("  my-folder  ") == "my-folder"


def test_trim_strips_tabs_and_newlines():
    """Tabs and newlines around the name are removed."""
    assert trim_sort_folder_name("\t\nmy-folder\n\t") == "my-folder"


def test_trim_preserves_internal_whitespace():
    """Whitespace inside the name is kept."""
    assert trim_sort_folder_name("  a b  ") == "a b"


@pytest.mark.parametrize("value", [None, 123])
def test_trim_rejects_non_str_input(value):
    """Non-string input raises TypeError."""
    with pytest.raises(TypeError):
        trim_sort_folder_name(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_trim_rejects_empty_or_whitespace_only(value):
    """Empty or whitespace-only input raises ValueError."""
    with pytest.raises(ValueError):
        trim_sort_folder_name(value)
