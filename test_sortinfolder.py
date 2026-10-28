import subprocess
import sys


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


def test_version_flag():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    assert "1.0" in output
