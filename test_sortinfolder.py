import subprocess
import sys
import os
import tempfile
import shutil
import hashlib
from PIL import Image
import piexif


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


def test_process_image_handles_duplicate_filenames():
    """Test that duplicate filenames are handled by adding numeric suffix."""
    from sortinfolder import process_image

    with tempfile.TemporaryDirectory() as tmpdir:
        basepath = os.path.join(tmpdir, "source")
        output_path = os.path.join(tmpdir, "output")
        os.makedirs(os.path.join(basepath, "sub1"))
        os.makedirs(os.path.join(basepath, "sub2"))

        # Create two JPG files with SAME name but DIFFERENT content in different subfolders
        # Both have same EXIF date (2024:06:15)
        test_date = "2024:06:15 10:30:00"

        # First file - red image
        file1_path = os.path.join(basepath, "sub1", "test.jpg")
        img1 = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: test_date,
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        exif_bytes = piexif.dump(exif_dict)
        img1.save(file1_path, "JPEG", exif=exif_bytes)

        # Second file - blue image (different content)
        file2_path = os.path.join(basepath, "sub2", "test.jpg")
        img2 = Image.new('RGB', (100, 100), color='blue')
        exif_bytes2 = piexif.dump(exif_dict)
        img2.save(file2_path, "JPEG", exif=exif_bytes2)

        # Process both images
        process_image(file1_path, basepath, output_path)
        process_image(file2_path, basepath, output_path)

        # Check results
        expected_folder = os.path.join(output_path, "2024/06/15")

        # First file should keep original name
        file1_output = os.path.join(expected_folder, "test.jpg")
        assert os.path.exists(file1_output), f"First file not found at {file1_output}"

        # Second file should get _1 suffix
        file2_output = os.path.join(expected_folder, "test_1.jpg")
        assert os.path.exists(file2_output), f"Second file not found at {file2_output}"

        # Verify both files exist and have different content (checksums)
        with open(file1_output, 'rb') as f:
            hash1 = hashlib.md5(f.read()).hexdigest()
        with open(file2_output, 'rb') as f:
            hash2 = hashlib.md5(f.read()).hexdigest()

        assert hash1 != hash2, "Files should have different content"

        # Verify content matches original (red vs blue)
        img1_out = Image.open(file1_output)
        img2_out = Image.open(file2_output)
        # Check a pixel color to verify content (PIL 'red' may be 254 not 255)
        r1, g1, b1 = img1_out.getpixel((50, 50))
        r2, g2, b2 = img2_out.getpixel((50, 50))
        assert r1 > 200 and g1 < 50 and b1 < 50, f"First file should be red, got ({r1}, {g1}, {b1})"
        assert r2 < 50 and g2 < 50 and b2 > 200, f"Second file should be blue, got ({r2}, {g2}, {b2})"

        print("Duplicate filename test passed!")


def test_process_image_supports_multiple_formats():
    """Test that process_image supports JPG, PNG, TIFF formats."""
    from sortinfolder import process_image, get_date_taken, add_relative_path_tag

    with tempfile.TemporaryDirectory() as tmpdir:
        basepath = os.path.join(tmpdir, "source")
        output_path = os.path.join(tmpdir, "output")
        os.makedirs(basepath)

        # Create test images in different formats
        test_date = (2024, 6, 15, 10, 30, 0)

        # Create JPG with EXIF date
        jpg_path = os.path.join(basepath, "test.jpg")
        img_jpg = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: "2024:06:15 10:30:00",
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        exif_bytes = piexif.dump(exif_dict)
        img_jpg.save(jpg_path, "JPEG", exif=exif_bytes)

        # Create PNG (no EXIF support in PIL for PNG)
        png_path = os.path.join(basepath, "test.png")
        img_png = Image.new('RGB', (100, 100), color='blue')
        img_png.save(png_path, "PNG")

        # Create TIFF with EXIF date
        tiff_path = os.path.join(basepath, "test.tiff")
        img_tiff = Image.new('RGB', (100, 100), color='green')
        exif_dict_tiff = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: "2024:06:15 10:30:00",
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        exif_bytes_tiff = piexif.dump(exif_dict_tiff)
        img_tiff.save(tiff_path, "TIFF", exif=exif_bytes_tiff)

        # Process each image
        process_image(jpg_path, basepath, output_path)
        process_image(png_path, basepath, output_path)
        process_image(tiff_path, basepath, output_path)

        # JPG and TIFF with EXIF date go to the expected date folder
        expected_folder = os.path.join(output_path, "2024/06/15")
        assert os.path.exists(os.path.join(expected_folder, "test.jpg")), "JPG not copied"
        assert os.path.exists(os.path.join(expected_folder, "test.tiff")), "TIFF not copied"

        # PNG has no EXIF - falls back to file creation date, but must be copied
        copied_files = []
        for root, dirs, files in os.walk(output_path):
            for f in files:
                copied_files.append(f)
        assert "test.png" in copied_files, "PNG not copied"

        # Verify JPG has RelativePath tag in EXIF UserComment
        jpg_output = os.path.join(expected_folder, "test.jpg")
        exif_data = piexif.load(jpg_output)
        user_comment = exif_data["Exif"].get(piexif.ExifIFD.UserComment, b'')
        assert b"RelativePath:" in user_comment, "JPG should have RelativePath tag"

        # Verify TIFF was copied but does NOT have RelativePath tag
        tiff_output = os.path.join(expected_folder, "test.tiff")
        assert os.path.exists(tiff_output), "TIFF should exist"

        print("All format tests passed!")


def test_cli_threads_and_dry_run():
    """Test CLI options for configurable thread count and dry-run mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        basepath = os.path.join(tmpdir, "source")
        output_path = os.path.join(tmpdir, "output")
        os.makedirs(basepath)

        # Create a test image
        test_date = "2024:06:15 10:30:00"
        file_path = os.path.join(basepath, "test.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: test_date,
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(file_path, "JPEG", exif=exif_bytes)

        # Run with --threads 5 --dry-run
        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath, output_path, "--threads", "5", "--dry-run"],
            capture_output=True,
            text=True,
        )

        # Combine stdout and stderr for checking (logging goes to stderr)
        combined_output = result.stdout + result.stderr

        # Check exit code is 0
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

        # Check output contains DRY RUN indication
        assert "DRY RUN" in combined_output, \
            f"Expected DRY RUN message in output. Got stdout: {result.stdout}, stderr: {result.stderr}"

        # Check output path does not exist or is empty (no files copied)
        if os.path.exists(output_path):
            files_in_output = []
            for root, dirs, files in os.walk(output_path):
                files_in_output.extend(files)
            assert len(files_in_output) == 0, f"Expected no files copied in dry-run, but found: {files_in_output}"

        # Check log shows what would happen (target paths, rotation, tags)
        assert "2024/06/15" in combined_output, f"Expected target date folder in dry-run output. Got: {combined_output}"
        assert "test.jpg" in combined_output, f"Expected filename in dry-run output. Got: {combined_output}"

        print("test_cli_threads_and_dry_run passed!")


def test_cli_invalid_threads_value():
    """Test that invalid thread values are rejected."""
    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "/tmp", "/tmp/out", "--threads", "0"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Expected non-zero exit code for threads=0"
    combined = result.stdout + result.stderr
    assert "threads" in combined.lower() or "thread" in combined.lower()

    result = subprocess.run(
        [sys.executable, "sortinfolder.py", "/tmp", "/tmp/out", "--threads", "101"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Expected non-zero exit code for threads=101"
    combined = result.stdout + result.stderr
    assert "threads" in combined.lower() or "thread" in combined.lower()

    print("test_cli_invalid_threads_value passed!")


def test_error_summary_and_exit_code():
    """Test that errors are collected and non-zero exit code is returned on failure."""
    import io
    import sys
    import logging
    from sortinfolder import sort_images, setup_logging

    with tempfile.TemporaryDirectory() as tmpdir:
        basepath = os.path.join(tmpdir, "source")
        output_path = os.path.join(tmpdir, "output")
        os.makedirs(basepath)

        # Create a valid image with EXIF date
        test_date = "2024:06:15 10:30:00"
        valid_file = os.path.join(basepath, "valid.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: test_date,
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(valid_file, "JPEG", exif=exif_bytes)

        # Create a corrupted/truncated image file (not a valid image)
        # This will cause an error when trying to process it
        corrupted_file = os.path.join(basepath, "corrupted.jpg")
        with open(corrupted_file, 'wb') as f:
            f.write(b"This is not a valid image file")

        # Set up logging to capture output using a custom handler
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter('%(asctime)s - [Thread %(thread)d] - %(levelname)s - %(message)s'))

        # Reset root logger
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        # sort_images should return (success_count, failure_count, errors_list)
        result = sort_images(basepath, output_path, threads=2, dry_run=False)

        # Check return value structure
        assert isinstance(result, tuple), "sort_images should return a tuple"
        assert len(result) == 3, "sort_images should return (success_count, failure_count, errors_list)"
        success_count, failure_count, errors_list = result

        # Check counts
        assert success_count == 1, f"Expected 1 success, got {success_count}"
        assert failure_count == 1, f"Expected 1 failure, got {failure_count}"
        assert len(errors_list) == 1, f"Expected 1 error in list, got {len(errors_list)}"

        # Check error details
        error = errors_list[0]
        assert "file" in error, "Error should contain file path"
        assert "type" in error, "Error should contain error type"
        assert "message" in error, "Error should contain error message"
        assert "corrupted.jpg" in error["file"], "Error should reference corrupted file"

        # Check log output contains summary
        combined_output = log_capture.getvalue()
        assert "Processed: 2" in combined_output, f"Expected 'Processed: 2' in output. Got: {combined_output}"
        assert "Succeeded: 1" in combined_output, f"Expected 'Succeeded: 1' in output. Got: {combined_output}"
        assert "Failed: 1" in combined_output, f"Expected 'Failed: 1' in output. Got: {combined_output}"

        # Verify valid image was still processed
        expected_folder = os.path.join(output_path, "2024/06/15")
        assert os.path.exists(os.path.join(expected_folder, "valid.jpg")), "Valid image should be processed despite error"

        print("test_error_summary_and_exit_code passed!")


def test_cli_exit_code_end_to_end():
    """Test CLI end-to-end: subprocess with corrupted file returns exit code 1,
    subprocess with only valid files returns exit code 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: CLI with corrupted file -> exit code 1, error summary in output
        basepath1 = os.path.join(tmpdir, "source1")
        output_path1 = os.path.join(tmpdir, "output1")
        os.makedirs(basepath1)

        test_date = "2024:06:15 10:30:00"
        valid_file = os.path.join(basepath1, "valid.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {},
            "Exif": {piexif.ExifIFD.DateTimeOriginal: test_date},
            "GPS": {}, "1st": {}, "thumbnail": None
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(valid_file, "JPEG", exif=exif_bytes)

        corrupted_file = os.path.join(basepath1, "corrupted.jpg")
        with open(corrupted_file, 'wb') as f:
            f.write(b"This is not a valid image file")

        result = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath1, output_path1],
            capture_output=True,
            text=True,
        )

        combined_output = result.stdout + result.stderr
        print(f"Test 1 (with corruption) - exit code: {result.returncode}")
        print(f"Test 1 stdout: {result.stdout}")
        print(f"Test 1 stderr: {result.stderr}")

        assert result.returncode == 1, f"Expected exit code 1 for corrupted file, got {result.returncode}"
        assert "Failed: 1" in combined_output, f"Expected 'Failed: 1' in output. Got: {combined_output}"
        assert "Processed: 2" in combined_output, f"Expected 'Processed: 2' in output. Got: {combined_output}"

        # Test 2: CLI with only valid files -> exit code 0
        basepath2 = os.path.join(tmpdir, "source2")
        output_path2 = os.path.join(tmpdir, "output2")
        os.makedirs(basepath2)

        valid_file2 = os.path.join(basepath2, "valid2.jpg")
        img2 = Image.new('RGB', (100, 100), color='blue')
        exif_bytes2 = piexif.dump(exif_dict)
        img2.save(valid_file2, "JPEG", exif=exif_bytes2)

        result2 = subprocess.run(
            [sys.executable, "sortinfolder.py", basepath2, output_path2],
            capture_output=True,
            text=True,
        )

        combined_output2 = result2.stdout + result2.stderr
        print(f"Test 2 (valid only) - exit code: {result2.returncode}")
        print(f"Test 2 stdout: {result2.stdout}")
        print(f"Test 2 stderr: {result2.stderr}")

        assert result2.returncode == 0, f"Expected exit code 0 for valid files only, got {result2.returncode}"
        assert "Failed: 0" in combined_output2, f"Expected 'Failed: 0' in output. Got: {combined_output2}"
        assert "Processed: 1" in combined_output2, f"Expected 'Processed: 1' in output. Got: {combined_output2}"

        # Verify the valid image was copied
        expected_folder = os.path.join(output_path2, "2024/06/15")
        assert os.path.exists(os.path.join(expected_folder, "valid2.jpg")), "Valid image should be copied"

        print("test_cli_exit_code_end_to_end passed!")


if __name__ == "__main__":
    test_help_shows_usage_and_examples()
    print("test_help_shows_usage_and_examples passed")

    test_process_image_handles_duplicate_filenames()
    print("test_process_image_handles_duplicate_filenames passed")

    test_process_image_supports_multiple_formats()
    print("test_process_image_supports_multiple_formats passed")

    test_cli_threads_and_dry_run()
    print("test_cli_threads_and_dry_run passed")

    test_cli_invalid_threads_value()
    print("test_cli_invalid_threads_value passed")

    test_error_summary_and_exit_code()
    print("test_error_summary_and_exit_code passed")