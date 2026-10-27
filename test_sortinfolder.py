import subprocess
import sys
import tempfile
import os


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


def test_nonexistent_input_folder_errors():
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = os.path.join(tmpdir, "does-not-exist")
        out = os.path.join(tmpdir, "out")
        result = subprocess.run(
            [sys.executable, "sortinfolder.py", nonexistent, out],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "does not exist" in result.stderr


def test_existing_input_folder_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
        inp = os.path.join(tmpdir, "in")
        os.makedirs(inp)
        out = os.path.join(tmpdir, "out")
        result = subprocess.run(
            [sys.executable, "sortinfolder.py", inp, out],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert os.path.isdir(out)
