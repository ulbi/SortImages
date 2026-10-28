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


def test_list_extensions_prints_sorted_unique_extensions(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"dummy image bytes")
    (tmp_path / "b.png").write_bytes(b"dummy image bytes")

    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--list-extensions", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == ["jpg", "png"]


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__]))
