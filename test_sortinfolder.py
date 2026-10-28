import subprocess
import sys
import tempfile
import os
from PIL import Image


def make_jpeg(path, width=1400, height=1000):
    """Create a JPEG larger than the 100KB processing threshold."""
    size = width * height * 3
    data = os.urandom(size)
    img = Image.frombytes("RGB", (width, height), data)
    img.save(path, "JPEG", quality=95)


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


def test_run_prints_processed_image_count():
    with tempfile.TemporaryDirectory() as tmp:
        basepath = os.path.join(tmp, "in")
        output_path = os.path.join(tmp, "out")
        os.makedirs(basepath)
        make_jpeg(os.path.join(basepath, "photo.jpg"))

        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Processed 1 images" in result.stdout


def test_run_prints_count_for_multiple_images():
    with tempfile.TemporaryDirectory() as tmp:
        basepath = os.path.join(tmp, "in")
        output_path = os.path.join(tmp, "out")
        os.makedirs(basepath)
        make_jpeg(os.path.join(basepath, "photo1.jpg"))
        make_jpeg(os.path.join(basepath, "photo2.jpg"))
        make_jpeg(os.path.join(basepath, "photo3.jpg"))

        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Processed 3 images" in result.stdout


def test_run_prints_nothing_when_no_images_processed():
    with tempfile.TemporaryDirectory() as tmp:
        basepath = os.path.join(tmp, "in")
        output_path = os.path.join(tmp, "out")
        os.makedirs(basepath)

        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Processed" not in result.stdout


def test_quiet_suppresses_processed_count():
    with tempfile.TemporaryDirectory() as tmp:
        basepath = os.path.join(tmp, "in")
        output_path = os.path.join(tmp, "out")
        os.makedirs(basepath)
        make_jpeg(os.path.join(basepath, "photo.jpg"))

        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path, "--quiet"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Processed" not in result.stdout
