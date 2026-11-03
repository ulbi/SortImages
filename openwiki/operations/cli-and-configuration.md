---
type: operations-reference
title: CLI, Configuration, and Operations
description: Operational reference for running sortinfolder.py — the argparse interface and its validation rules, thread-count bounds, logging setup and levels, dry-run mode, exit-code behavior, the CI container, and the copy-only (additive) safety model.
tags: [operations, cli, argparse, logging, exit-codes, ci, configuration]
verified:
  - by: openwiki/0.7.3
    at: 2026-11-03T04:36:59.554Z
sources:
  - id: openwiki-source-11ab5406a11e454dd2e00511
    resource: repo://.ci/ci.yaml
  - id: openwiki-source-7c04a8ec2195a4cf40e7c237
    resource: repo://.ci/test.Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-edab51d2990d321ab74ffdac
    resource: repo://sortinfolder.py
  - id: openwiki-source-48eb19a4c1e45a7d3b04236a
    resource: repo://test_sortinfolder.py
generated: { by: "openwiki/0.7.3", at: "2026-11-03T04:36:59.554Z" }
---

# CLI, Configuration, and Operations

`sortinfolder.py` is operated entirely from the command line: there are no configuration files, no environment variables, and no persistent state of its own. Every knob is a CLI flag parsed by `main()`, and the only runtime configuration is which directory to read, which directory to write, how loudly to log, how many worker threads to use, and whether to simulate instead of copying. This page is the operational reference for that surface.

## The command line

```
python sortinfolder.py [basepath] [output_path] [--log LEVEL] [--threads N] [--dry-run]
```

The parser is built with `prog="sortimages"` and includes an epilog with three examples:

```
sortimages /data/photos /data/sorted
sortimages /data/photos /data/sorted --log DEBUG
sortimages /data/photos /data/sorted --threads 5 --dry-run
```

| Argument | Type | Default | Meaning |
| --- | --- | --- | --- |
| `basepath` (positional) | str | — | The base path where the images are located. |
| `output_path` (positional) | str | — | The output path where images will be copied to. |
| `--log` | str | `INFO` | Logging level name (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `--threads` | int | `30` | Number of worker threads (validated to 1–100). |
| `--dry-run` | flag | `False` | Simulate processing without copying files. |

The two positional arguments are required; running without them prints argparse usage and exits with argparse's standard error code 2 before any processing begins.

## Argument validation rules

Validation is split between `main()` and `sort_images()`, and the two follow different failure styles:

- **`--log` is validated in `main()` immediately after parsing.** The string is upper-cased and looked up via `getattr(logging, args.log.upper(), None)`. If the result is not an `int`, `main()` raises `TypeError(f"Invalid log level: {args.log}")` — before any logging is configured or any file is touched. Valid names are the standard `logging` module level attributes (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, and their numeric aliases such as `logging.NOTSET`).
- **`--threads` is *not* validated in `main()`.** It is passed through to `sort_images(basepath, output_path, threads=args.threads, dry_run=args.dry_run)`, which enforces the bound itself: `if not 1 <= threads <= 100: raise ValueError(...)`. Out-of-range values therefore fail inside the orchestration layer, not at parse time. `test_cli_invalid_threads_value` drives this end-to-end via subprocesses: `--threads 0` and `--threads 101` both produce a non-zero exit code and output mentioning threads.

There is no upper validation on the two path arguments — a nonexistent `basepath` simply makes `os.walk` yield nothing (an empty run), while a nonexistent `output_path` is created automatically by `sort_images` (`os.makedirs(output_path)`) before any file is submitted.

## Exit codes

`main()` exits with a single well-defined convention:

- **Exit 0** on success. `main()` does not call `sys.exit(0)` explicitly; falling through the end of `main()` produces the interpreter's default exit code 0.
- **Exit 1** only when `failure_count > 0`, i.e. when at least one submitted file raised an exception in its worker thread. This is the only condition that triggers `sys.exit(1)`.

Note that per-file errors do not abort the run. `sort_images` catches every worker exception (`except Exception`), appends a structured record `{"file": ..., "type": ..., "message": ...}` to `errors_list`, logs it at error level, and continues; the summary line `Processed: N, Succeeded: N, Failed: N` is always logged, and the exit code reflects the aggregate, not the first error. Both paths are covered end-to-end by `test_cli_exit_code_end_to_end`, which runs the CLI as a subprocess and asserts exit code 1 for a run containing a corrupted file and exit code 0 for a run of valid files only. Exit-code semantics and the error-summary structure are also asserted in `test_error_summary_and_exit_code` (see [Test Suite](../testing/test-suite.md)).

## Logging

Logging is configured by `setup_logging(level)`, which is called once from `main()` after the `--log` value is resolved to a numeric level. It uses a single `logging.basicConfig` call with a thread-aware format:

```
%(asctime)s - [Thread %(thread)d] - %(levelname)s - %(message)s
```

The `Thread` field is what makes concurrent output readable: each log line identifies which of the up-to-100 worker threads emitted it, since workers run inside a `ThreadPoolExecutor`. All log output goes to stderr via the default `basicConfig` stream handler.

Per-level usage in the pipeline:

| Level | What appears at that level |
| --- | --- |
| `DEBUG` | Quiet-path diagnostics: unsupported-format skips, EXIF orientation lookups (`Found EXIF Orientation: N`), rotation decisions (`Image rotated 180 degrees`, `No rotation required`), extracted EXIF date strings, missing-orientation-tag errors. |
| `INFO` | Normal operation: the argument echo (`Script arguments - Basepath: ...`), dry-run banner (`DRY RUN MODE - Simulating processing without copying files`), directory creation, filename-collision notices (`Filename collision detected for ...`), every copy (`Copied X to Y`), the unsupported-for-tagging notice, and the final `Processed: N, Succeeded: N, Failed: N` summary. |
| `WARNING` | Recoverable degradation: EXIF `DateTimeOriginal` missing so file creation time is used instead, and dry-run failures to pre-check rotation. |
| `ERROR` | Per-file failures logged by `sort_images` (`Failed to process X: Type: message`), truncated-image reports, tagging struct errors, and general rotation errors. |

The default `INFO` level is deliberately chosen for production use: it is the quietest level that still logs every copy and the run summary, which is the minimum an operator needs to reconcile the output tree after a run.

## Dry-run mode

`--dry-run` changes `process_image` into a pure planning mode; nothing is written except the output directory itself (see the caveat below). The differences:

1. `sort_images` logs the banner `DRY RUN MODE - Simulating processing without copying files`.
2. Date extraction still runs, so the would-be `%Y/%m/%d` destination is computed — but the date folder is **not** created (`os.makedirs` is skipped in dry-run).
3. Instead of copying, the worker logs `DRY RUN: Would copy <file> to <new_file_path>` (including any `_N` collision suffix that would be applied).
4. Instead of rotating, it opens the source read-only, reads the EXIF orientation, and logs `DRY RUN: Would rotate image ... by N degrees` (180/270/90 for orientations 3/6/8) or `DRY RUN: No rotation needed for ...`. If the image cannot be opened, it logs a warning `DRY RUN: Could not check rotation for ...` and continues.
5. Instead of tagging, it logs `DRY RUN: Would add RelativePath tag: RelativePath:<value> to <path>` for `.jpg`/`.jpeg`, or `DRY RUN: Would skip tag for ... (format not supported for tagging)` for other formats.

`test_cli_threads_and_dry_run` verifies the contract: with `--threads 5 --dry-run` the CLI exits 0, output contains `DRY RUN` plus the target date folder and filename, and the output directory contains **zero files**. Dry-run is therefore safe to point at a real output directory used by previous real runs — it adds nothing, copies nothing, and modifies nothing (though `sort_images` still creates the top-level `output_path` if it does not exist).

## Operational safety model: additive, copy-only

The README's Note says it plainly: *"Make sure to back up your images before processing."* The reason this is safe advice rather than mandatory is the tool's fundamental design: **the source tree is never modified**. All mutation (EXIF-based rotation and `RelativePath` tagging) is applied only to the file *after* it has been copied with `shutil.copy2` into `output_path`; the operations then run against `new_file_path`, never the original. The result is additive:

- New directories (`output_path/YYYY/MM/DD`) and new files appear in the output tree.
- If a run is interrupted, the source tree is untouched and partially-written output files can simply be deleted; re-running the tool re-copies everything (already-copied files collide and get `_N` suffixes rather than being overwritten — there is no overwrite or dedup logic).
- `shutil.copy2` preserves metadata (mtime, permissions), so the copied file keeps its original timestamps even after EXIF edits.

Backing up is still recommended because the tool runs concurrently (up to 100 threads by default 30) and because a misconfigured `output_path` that overlaps `basepath` would create output *inside* the source tree — the tool does not detect or prevent that overlap. Operators should pass distinct paths.

## CI container

Continuous integration for this project is defined in two small files:

- **`.ci/test.Dockerfile`** — builds the test image from `python:3.12-slim`, installs the three runtime dependencies with `pip install --no-cache-dir Pillow exifread piexif`, and sets `WORKDIR /workspace`. No other system packages or test tooling are installed.
- **`.ci/ci.yaml`** — points `image.dockerfile` at `.ci/test.Dockerfile` and defines a single `unit` check whose `cmd` is the array `["python", "-c", "import sortinfolder"]` (executed directly, without a shell). Importing the module compiles and loads it, so the CI gate is effectively "the module imports cleanly in a stock Python 3.12 slim image with Pillow, exifread, and piexif available".

This is why the module must remain importable with no top-level side effects: the `if __name__ == "__main__": main()` guard is the only thing that keeps `import sortinfolder` from running a sort. For the behavioral tests that run on top of this gate, see [Test Suite](../testing/test-suite.md).

## End-to-end operational flow

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart TD
    START["python sortinfolder.py basepath output_path --log --threads --dry-run"] --> PARSE["main() parses argparse"]
    PARSE --> LOGCHK{"--log resolves to int?"}
    LOGCHK -- "no" --> TYPEERR["TypeError: Invalid log level - exit before any work"]
    LOGCHK -- "yes" --> SETUP["setup_logging with resolved level"]
    SETUP --> SI["sort_images validates threads 1-100"]
    SI -- "out of range" --> VALERR["ValueError raised to caller"]
    SI -- "valid" --> WALK["os.walk basepath, create output_path if missing"]
    WALK --> POOL["ThreadPoolExecutor with N workers"]
    POOL --> RES["count successes and failures, collect error dicts"]
    RES --> SUM["log summary Processed Succeeded Failed"]
    SUM --> EXIT{"failure_count > 0?"}
    EXIT -- "yes" --> ONE["sys.exit 1"]
    EXIT -- "no" --> ZERO["exit 0"]
```

*Caption: from CLI invocation to exit code — log-level validation in `main()`, thread validation in `sort_images()`, and the aggregate failure rule that determines exit 0 or 1.*

## Related pages

- Getting started and installation: [Quickstart](../quickstart.md)
- How the sorting, rotation, and tagging pipeline works: [Sorting Pipeline](../workflows/sorting-pipeline.md)
- System structure and layering: [Architecture Overview](../architecture/overview.md)
- Behavioral tests behind the guarantees above: [Test Suite](../testing/test-suite.md)
