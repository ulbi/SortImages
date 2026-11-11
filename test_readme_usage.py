import pathlib
import re

import pytest

README = pathlib.Path(__file__).parent / "README.md"
TEST_DOCKERFILE = pathlib.Path(__file__).parent / ".ci" / "test.Dockerfile"

BUILD_CMD = "docker build -t sortimages-test -f .ci/test.Dockerfile ."
RUN_PREFIX = "docker run --rm -v \"$PWD\":/workspace sortimages-test"
RUN_SORTINFOLDER = f"{RUN_PREFIX} python -m pytest test_sortinfolder.py"
RUN_README_USAGE = f"{RUN_PREFIX} python -m pytest test_readme_usage.py"


@pytest.fixture(scope="module")
def readme_text():
    assert README.exists(), "README.md fehlt im Repository"
    return README.read_text(encoding="utf-8")


def find_section(text, heading):
    pattern = re.compile(
        rf"^#+\s*{re.escape(heading)}\b.*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    assert match is not None, (
        f"README.md enthaelt keinen Abschnitt '{heading}'"
    )
    start = match.end()
    next_heading = re.search(r"^#+\s", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def test_readme_has_test_section(readme_text):
    find_section(readme_text, "Tests ausfuehren")


def test_readme_documents_docker_build(readme_text):
    section = find_section(readme_text, "Tests ausfuehren")
    assert ".ci/test.Dockerfile" in section
    assert BUILD_CMD in section


def test_readme_documents_docker_run_for_sortinfolder(readme_text):
    section = find_section(readme_text, "Tests ausfuehren")
    assert "docker run" in section
    assert "/workspace" in section
    assert RUN_SORTINFOLDER in section


def test_readme_documents_docker_run_for_readme_usage(readme_text):
    section = find_section(readme_text, "Tests ausfuehren")
    assert "docker run" in section
    assert "/workspace" in section
    assert RUN_README_USAGE in section


def test_test_dockerfile_installs_pytest():
    assert TEST_DOCKERFILE.exists(), ".ci/test.Dockerfile fehlt im Repository"
    dockerfile_text = TEST_DOCKERFILE.read_text(encoding="utf-8")
    pip_install_lines = [
        line.strip()
        for line in dockerfile_text.splitlines()
        if line.strip().startswith("RUN pip install")
    ]
    assert pip_install_lines, (
        ".ci/test.Dockerfile enthaelt keine pip-install-Zeile"
    )
    assert any("pytest" in line.split() for line in pip_install_lines), (
        ".ci/test.Dockerfile installiert pytest in der pip-install-Zeile nicht"
    )
