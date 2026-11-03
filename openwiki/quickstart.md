---
type: entry-point
title: Quickstart
description: Entry point for the OpenWiki of this repository — a single-file EXIF-based photo sorter. Covers what the tool does, how to install its dependencies, how to run the CLI, and where to go next in the wiki.
tags: [quickstart, installation, cli, python, exif]
verified:
  - by: openwiki/0.7.3
    at: 2026-11-03T04:36:59.554Z
sources:
  - id: openwiki-source-7c04a8ec2195a4cf40e7c237
    resource: repo://.ci/test.Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-edab51d2990d321ab74ffdac
    resource: repo://sortinfolder.py
generated: { by: "openwiki/0.7.3", at: "2026-11-03T04:36:59.554Z" }
---

# Quickstart

This repository is a single-file Python tool, [`sortinfolder.py`](../sortinfolder.py), that sorts image files into a `<year>/<month>/<day>` folder hierarchy based on their EXIF capture date. For each image it can also correct orientation from the EXIF orientation tag and stamp the source-relative path into the JPEG EXIF `UserComment` field. The tool is designed for JPEG images but also skips-or-handles a set of other common formats.

## Requirements

- Python 3.x (the CI image uses Python 3.12)
- [Pillow](https://pypi.org/project/Pillow/) — image opening, rotation, saving
- [exifread](https://pypi.org/project/exifread/) — reading the EXIF `DateTimeOriginal` tag
- [piexif](https://pypi.org/project/piexif/) — writing the `RelativePath` tag into JPEG EXIF data

Install dependencies with pip:

```bash
pip install Pillow exifread piexif
```

## Running the sorter

The exact invocation from the README:

```bash
python sortinfolder.py [basepath] [output_path] [--log LEVEL] [--threads N] [--dry-run]
```

- `basepath` — directory where your images are stored (searched recursively).
- `output_path` — directory where processed images will be saved.
- `--log LEVEL` — logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default `INFO`).
- `--threads N` — number of worker threads, 1–100 (default 30).
- `--dry-run` — simulate processing without copying files.

For example:

```bash
python sortinfolder.py /data/photos /data/sorted --threads 5 --dry-run
```

The process exits with code 1 if any file failed to process; the script's `main()` argparse surface defines the positional arguments `basepath` and `output_path` plus the three optional flags above. See [CLI, Configuration, and Operations](operations/cli-and-configuration.md) for validation rules, exit codes, and logging details.

## How it works, in one paragraph

`main()` parses arguments and calls `sort_images()`, which walks `basepath` recursively, fans the discovered files out to a thread pool, and processes each file: it extracts the capture date from EXIF (`DateTimeOriginal`, with the file creation time as fallback), creates a `year/month/day` folder, resolves filename collisions with `_N` suffixes, copies the file, rotates it according to the EXIF orientation tag, and (for JPEG) appends the original relative path as a `RelativePath:` EXIF `UserComment` tag. With `--dry-run`, the same decisions are logged without touching the filesystem. The [Sorting Pipeline](workflows/sorting-pipeline.md) page traces this end to end.

## Where to go next

- [Architecture Overview](architecture/overview.md) — the module map: public functions of `sortinfolder.py`, layering from CLI entry down to per-file processing, and the external dependency roles.
- [EXIF and Metadata](concepts/exif-and-metadata.md) — orientation tags (3 = 180°, 6 = 270°, 8 = 90°), `DateTimeOriginal` extraction and its ctime fallback, and the `RelativePath` `UserComment` tag written with piexif (JPEG only).
- [Sorting Pipeline](workflows/sorting-pipeline.md) — the end-to-end flow: `os.walk` discovery, thread-pool fan-out, per-file steps, collision handling, dry-run behavior, and the `(success, failure, errors)` result tuple.
- [CLI, Configuration, and Operations](operations/cli-and-configuration.md) — argparse interface and validation rules, thread-count bounds, logging setup, dry-run mode, exit codes, and the CI container.
- [Test Suite](testing/test-suite.md) — the pytest suite in `test_sortinfolder.py`, its fixture patterns, and how CI exercises the code.
