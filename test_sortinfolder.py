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


def test_nonexistent_folder_prints_error_to_stderr_and_exits_nonzero(tmp_path):
    missing_folder = tmp_path / "does_not_exist"
    output_folder = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", str(missing_folder), str(output_folder)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "does not exist" in result.stderr
    assert str(missing_folder) in result.stderr
    assert not output_folder.exists()
