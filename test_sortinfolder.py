import subprocess
import sys
from pathlib import Path

README = Path(__file__).parent / "README.md"


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


def test_readme_references_real_script_filename():
    content = README.read_text()
    assert "sortinfolder.py" in content
    assert "image_processor.py" not in content


def test_readme_cli_example_shows_positional_args_and_log_flag():
    content = README.read_text()
    assert "python sortinfolder.py" in content
    assert "[basepath] [output_path]" in content
    assert "--log" in content
