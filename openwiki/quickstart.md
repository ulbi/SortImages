---
type: entry-point
title: Quickstart
description: Repository entry point for the OpenWiki of this repository — install the three manual runtime dependencies, preview a run safely with --dry-run, understand the dated output layout, and route readers to architecture, pipeline, metadata, CLI/operations, agent-guidance, and test pages.
tags: [quickstart, installation, cli, python, exif, dry-run]
sources:
  - id: openwiki-source-7c04a8ec2195a4cf40e7c237
    resource: repo://.ci/test.Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-edab51d2990d321ab74ffdac
    resource: repo://sortinfolder.py
verified:
  - by: openwiki/0.9.0
    at: 2026-11-11T09:15:33.931Z
generated: { by: "openwiki/0.9.0", at: "2026-11-11T09:15:33.931Z" }
---

# Quickstart

This repository is a single-file Python tool, [`sortinfolder.py`](../sortinfolder.py), that sorts image files into a `<year>/<month>/<day>` folder hierarchy based on their EXIF capture date. For each image it can also correct orientation from the EXIF orientation tag and stamp the source-relative path into the JPEG EXIF `UserComment` field. The tool is additive: it copies sources into a new output tree, never edits or deletes anything under `basepath`, and never overwrites an existing destination (same-named files receive `_1`, `_2`, … suffixes).

Because source code and tests are authoritative when wording conflicts with behavior, note that the tool handles more than just JPEG: `SUPPORTED_FORMATS` covers `.jpg`, `.jpeg`, `.png`, `.heic`, `.tiff`, `.tif`, `.bmp`, and `.webp`. Only `.jpg`/`.jpeg` files receive the `RelativePath` tag; all other supported formats are copied and dated but not tagged. See [Architecture Overview](architecture/overview.md) and [Sorting Pipeline](workflows/sorting-pipeline.md) for details.

## Installation

There is no `requirements.txt`, `pyproject.toml`, or `setup.py` in the repository, so the three runtime dependencies are installed manually and are unpinned outside the CI image:

```bash
pip install Pillow exifread piexif
```

- [Pillow](https://pypi.org/project/Pillow/) — image opening, rotation, saving
- [exifread](https://pypi.org/project/exifread/) — reading the EXIF `DateTimeOriginal` tag
- [piexif](https://pypi.org/project/piexif/) — writing the `RelativePath` tag into JPEG EXIF data

<!-- openwiki: broken internal link [.ci/test.Dockerfile] file ".ci/test.Dockerfile" does not exist. Fix the href or restore the target, then delete this comment. -->
Python 3.x is required; the CI image is `python:3.12-slim` and installs exactly these three packages ([`.ci/test.Dockerfile`](.ci/test.Dockerfile)).

## Safe usage order — validate with --dry-run first

The tool is copy-only and additive, but a real run still writes into `output_path`, so always preview before copying:

```bash
python sortinfolder.py /data/photos /data/sorted --threads 5 --dry-run
```

`--dry-run` logs every planned decision — the destination `YYYY/MM/DD` folder, any `_N` collision suffix, the rotation angle, and the `RelativePath` tag — without copying, rotating, or tagging anything. The only filesystem side effect is that `output_path` itself may be created if missing; no date folders and no image files are created below it. When the preview looks right, run the same command without `--dry-run` to perform the copy.

Full invocation:

```bash
python sortinfolder.py [basepath] [output_path] [--log LEVEL] [--threads N] [--dry-run]
```

- `basepath` — directory where your images are stored (searched recursively).
- `output_path` — directory where processed images will be saved.
- `--log LEVEL` — logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default `INFO`).
- `--threads N` — number of worker threads, 1–100 (default 30).
- `--dry-run` — simulate processing without copying files.

The process exits with code 1 if any submitted file failed to process; otherwise it exits 0. See [CLI, Configuration, and Operations](operations/cli-and-configuration.md) for validation rules, exit codes, and logging details.

## What the output looks like

A real run produces:

```
<output_path>/
  2024/
    06/
      15/
        vacation.jpg
        vacation_1.jpg          # collision suffix from another source folder
```

Each file sits under `YYYY/MM/DD` derived from its EXIF `DateTimeOriginal`, falling back to the file creation time when that tag is missing. JPEG copies additionally carry a `RelativePath:` line in their EXIF `UserComment` recording where the file lived under `basepath`. The source tree is never modified: rotation and tagging rewrite only the copied destination.

## Where to go next

- [Architecture Overview](architecture/overview.md) — the module map: public functions of `sortinfolder.py`, layering from CLI entry down to per-file processing, the `SUPPORTED_FORMATS` gate, dependency roles, and the filesystem-only state model.
- [EXIF and Metadata](concepts/exif-and-metadata.md) — orientation tags (3 = 180°, 6 = 270°, 8 = 90°), `DateTimeOriginal` extraction and its ctime fallback, and the `RelativePath` `UserComment` tag written with piexif (JPEG only).
- [Sorting Pipeline](workflows/sorting-pipeline.md) — the end-to-end flow: `os.walk` discovery, thread-pool fan-out, per-file steps, collision handling, dry-run behavior, and the `(success, failure, errors)` result tuple.
- [CLI, Configuration, and Operations](operations/cli-and-configuration.md) — argparse interface and validation rules, thread-count bounds, logging setup, dry-run mode, exit codes, the CI container, and the additive copy-only safety model.
- [Repository Guidance and Coding-Agent Configuration](operations/agent-configuration.md) — repository-level instructions and tooling that affect how a coding agent works here: `AGENTS.md` OpenWiki rules and source-of-truth policy, LiteLLM provider settings in `.codex/config.toml` and `opencode.json`, the `.optio` setup helper, and validation expectations.
- [Test Suite](testing/test-suite.md) — the pytest suite in `test_sortinfolder.py`, its fixture patterns, direct-import versus subprocess test styles, and the minimal CI import gate.
