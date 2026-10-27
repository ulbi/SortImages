import datetime
import os
import subprocess
import sys

from PIL import Image

import sortinfolder

LARGE_SIZE = (1600, 1600)


def _make_jpg(path, size=LARGE_SIZE):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = os.urandom(size[0] * size[1] * 3)
    img = Image.frombytes("RGB", size, data)
    img.save(path, "JPEG", quality=95)
    assert path.stat().st_size > 100 * 1024
    return path


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


def test_help_documents_dry_run_flag():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--dry-run" in result.stdout


def test_dry_run_prints_planned_moves_without_moving(tmp_path, monkeypatch, capsys):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    image = _make_jpg(source_dir / "IMG_0001.jpg")

    monkeypatch.setattr(
        sortinfolder,
        "get_date_taken",
        lambda path: datetime.datetime(2020, 5, 17, 10, 30, 0),
    )

    sortinfolder.sort_images(str(source_dir), str(output_dir), dry_run=True)

    captured = capsys.readouterr()
    expected_destination = os.path.join(
        str(output_dir), "2020", "05", "17", "IMG_0001.jpg"
    )
    assert f"Move {image} -> {expected_destination}" in captured.out
    assert image.exists()
    assert not output_dir.exists()


def test_dry_run_via_cli_prints_moves_without_moving(tmp_path):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    image = _make_jpg(source_dir / "IMG_0002.jpg")

    result = subprocess.run(
        [
            sys.executable,
            "sortinfolder.py",
            str(source_dir),
            str(output_dir),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"Move {image} -> " in result.stdout
    assert image.exists()
    assert not output_dir.exists()


def test_without_dry_run_moves_files(tmp_path, monkeypatch):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    image = _make_jpg(source_dir / "IMG_0003.jpg")

    monkeypatch.setattr(
        sortinfolder,
        "get_date_taken",
        lambda path: datetime.datetime(2020, 5, 17, 10, 30, 0),
    )

    sortinfolder.sort_images(str(source_dir), str(output_dir))

    destination = output_dir / "2020" / "05" / "17" / "IMG_0003.jpg"
    assert destination.exists()
    assert image.exists()


def test_dry_run_skips_ineligible_files(tmp_path, monkeypatch, capsys):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    _make_jpg(source_dir / "IMG_0004.jpg")
    small = source_dir / "small.jpg"
    small.write_bytes(b"tiny")
    png = source_dir / "image.png"
    png.write_bytes(b"not an image")

    monkeypatch.setattr(
        sortinfolder,
        "get_date_taken",
        lambda path: datetime.datetime(2020, 5, 17, 10, 30, 0),
    )

    sortinfolder.sort_images(str(source_dir), str(output_dir), dry_run=True)

    captured = capsys.readouterr()
    assert f"Move {small} -> " not in captured.out
    assert f"Move {png} -> " not in captured.out
    assert f"Move {source_dir / 'IMG_0004.jpg'} -> " in captured.out
    assert not output_dir.exists()


def test_help_documents_stats_flag():
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "--stats" in result.stdout


def test_stats_prints_summary_after_sorting(tmp_path, monkeypatch, capsys):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    _make_jpg(source_dir / "IMG_0001.jpg")
    _make_jpg(source_dir / "IMG_0002.jpg")
    small = source_dir / "small.jpg"
    small.write_bytes(b"tiny")
    png = source_dir / "image.png"
    png.write_bytes(b"not an image")

    monkeypatch.setattr(
        sortinfolder,
        "get_date_taken",
        lambda path: datetime.datetime(2020, 5, 17, 10, 30, 0),
    )
    monkeypatch.setattr(
        sortinfolder, "rotate_image_according_to_exif", lambda path: None
    )
    monkeypatch.setattr(
        sortinfolder, "add_relative_path_tag", lambda path, relative_path: None
    )

    sortinfolder.sort_images(str(source_dir), str(output_dir), stats=True)

    captured = capsys.readouterr()
    assert "Files scanned:" in captured.out
    assert "Images processed:" in captured.out
    assert "Skipped:" in captured.out
    assert "Elapsed time:" in captured.out
    assert "4" in captured.out
    assert "2" in captured.out
    assert (output_dir / "2020" / "05" / "17" / "IMG_0001.jpg").exists()


def test_stats_via_cli_prints_summary(tmp_path):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    image = _make_jpg(source_dir / "IMG_0002.jpg")

    result = subprocess.run(
        [
            sys.executable,
            "sortinfolder.py",
            str(source_dir),
            str(output_dir),
            "--stats",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Files scanned:" in result.stdout
    assert "Images processed:" in result.stdout
    assert "Skipped:" in result.stdout
    assert "Elapsed time:" in result.stdout
    assert sorted(os.listdir(str(output_dir / "2026" / "10" / "27"))) == sorted(
        [os.path.basename(str(image))]
    )


def test_without_stats_prints_no_summary(tmp_path, monkeypatch, capsys):
    source_dir = tmp_path / "photos"
    output_dir = tmp_path / "sorted"
    _make_jpg(source_dir / "IMG_0001.jpg")

    monkeypatch.setattr(
        sortinfolder,
        "get_date_taken",
        lambda path: datetime.datetime(2020, 5, 17, 10, 30, 0),
    )
    monkeypatch.setattr(
        sortinfolder, "rotate_image_according_to_exif", lambda path: None
    )
    monkeypatch.setattr(
        sortinfolder, "add_relative_path_tag", lambda path, relative_path: None
    )

    sortinfolder.sort_images(str(source_dir), str(output_dir))

    captured = capsys.readouterr()
    assert "Files scanned:" not in captured.out
    assert "Elapsed time:" not in captured.out
    assert (output_dir / "2020" / "05" / "17" / "IMG_0001.jpg").exists()
