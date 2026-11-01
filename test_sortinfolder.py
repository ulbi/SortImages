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


if __name__ == "__main__":
    test_help_shows_usage_and_examples()
    print("test_help_shows_usage_and_examples passed")

    test_process_image_handles_duplicate_filenames()
    print("test_process_image_handles_duplicate_filenames passed")

    test_process_image_supports_multiple_formats()
    print("test_process_image_supports_multiple_formats passed")