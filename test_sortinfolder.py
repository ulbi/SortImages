import subprocess
import sys
import unittest


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


def test_version_flag_prints_default_version_and_exits_zero():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "0.1.0"


def test_version_flag_uses_defined_version_module_attribute():
    code = """
import sys
sys.argv = ["sortinfolder.py", "--version"]
import sortinfolder
sortinfolder.__version__ = "1.2.3"
sortinfolder.main()
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "1.2.3"


if __name__ == "__main__":
    suite = unittest.TestSuite()
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            suite.addTest(unittest.FunctionTestCase(value))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
