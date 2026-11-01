import pytest
from sortinfolder import SUPPORTED_FORMATS


def test_readme_lists_supported_formats():
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    assert "## Usage" in readme, "README missing '## Usage' section"

    assert "python sortinfolder.py" in readme, "README missing execution command"

    for fmt in SUPPORTED_FORMATS:
        assert fmt in readme, f"README missing supported format: {fmt}"