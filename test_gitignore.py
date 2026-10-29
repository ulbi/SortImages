import pathlib
import subprocess

GITIGNORE = pathlib.Path(".gitignore")


def test_gitignore_has_python_cache_rules():
    rules = GITIGNORE.read_text()
    assert "__pycache__/" in rules
    assert "*.pyc" in rules


def test_python_cache_files_are_ignored_by_git():
    result = subprocess.run(
        ["git", "check-ignore", "foo.pyc", "__pycache__/foo.pyc"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0