from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _gitignore_lines():
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.is_file(), ".gitignore file does not exist"
    return gitignore.read_text().splitlines()


def test_gitignore_ignores_python_cache_dir():
    lines = _gitignore_lines()
    assert any(line.strip() == "/__pycache__/" for line in lines)


def test_gitignore_ignores_pyc_files():
    lines = _gitignore_lines()
    assert any(line.strip() == "*.pyc" for line in lines)


def test_gitignore_ignores_ds_store():
    lines = _gitignore_lines()
    assert any(line.strip() == ".DS_Store" for line in lines)