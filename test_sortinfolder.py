import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(REPO_ROOT, "src", "sortinfolder.py")
SOURCE_FILE = os.path.join(REPO_ROOT, "src", "sortinfolder.py")

# Must stay in sync with the `unit.cmd` defined in .ci/ci.yaml: the SQL
# build runs this expression and expects exactly the first 30 lines of
# src/sortinfolder.py on stdout, and nothing else.
CI_UNIT_EXPR = (
    "import sys; "
    "sys.stdout.writelines(list(open('src/sortinfolder.py', encoding='utf-8'))[:30])"
)


def test_help_shows_usage_and_examples():
    result = subprocess.run(
        [sys.executable, SCRIPT, "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    assert "usage: sortimages" in output
    assert "options:" in output
    assert "Examples:" in output


def test_ci_unit_command_prints_first_30_lines_of_source():
    """Machine-readable test for the SQL build: the unit test defined in
    .ci/ci.yaml must print the first 30 lines of src/sortinfolder.py to
    stdout, and nothing else."""
    result = subprocess.run(
        [sys.executable, "-c", CI_UNIT_EXPR],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    expected = "".join(open(SOURCE_FILE, encoding="utf-8").readlines()[:30])
    assert result.stdout == expected
    assert result.stderr == ""
