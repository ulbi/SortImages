from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def test_readme_usage_example_references_existing_script():
    readme = (REPO_ROOT / "README.md").read_text()
    usage_block = readme.split("```")[1]
    assert "sortinfolder.py" in usage_block, (
        "README usage example must reference the actual script sortinfolder.py"
    )
    assert "image_processor.py" not in usage_block, (
        "README usage example must not reference the non-existent image_processor.py"
    )