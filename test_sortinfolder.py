import os
import subprocess
import sys
import tempfile


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


def test_missing_basepath_prints_error_and_exits_nonzero():
    missing_folder = os.path.join(tempfile.gettempdir(), "does-not-exist-f6ddaf58")
    if os.path.exists(missing_folder):
        os.rmdir(missing_folder)
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", missing_folder, "output"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "does not exist" in result.stderr
    assert missing_folder in result.stderr


def test_existing_folder_is_sorted_without_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        basepath = os.path.join(tmpdir, "photos")
        output_path = os.path.join(tmpdir, "sorted")
        os.makedirs(basepath)
        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "does not exist" not in result.stderr
