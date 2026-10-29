import os


def _gitignore_content():
    path = os.path.join(os.path.dirname(__file__), ".gitignore")
    with open(path) as f:
        return f.read()


def test_gitignore_ignores_pycache():
    assert "__pycache__/" in _gitignore_content()


def test_gitignore_ignores_pyc_files():
    assert "*.pyc" in _gitignore_content()


def test_gitignore_ignores_ds_store():
    assert ".DS_Store" in _gitignore_content()