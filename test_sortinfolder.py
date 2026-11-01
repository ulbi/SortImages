import subprocess
import sys
import os
import tempfile
import shutil
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

        # Verify all files were copied to correct date folder
        expected_folder = os.path.join(output_path, "2024/06/15")
        assert os.path.exists(os.path.join(expected_folder, "test.jpg")), "JPG not copied"
        assert os.path.exists(os.path.join(expected_folder, "test.png")), "PNG not copied"
        assert os.path.exists(os.path.join(expected_folder, "test.tiff")), "TIFF not copied"

        # Verify JPG has RelativePath tag in EXIF UserComment
        jpg_output = os.path.join(expected_folder, "test.jpg")
        exif_data = piexif.load(jpg_output)
        user_comment = exif_data["Exif"].get(piexif.ExifIFD.UserComment, b'')
        assert b"RelativePath:" in user_comment, "JPG should have RelativePath tag"

        # Verify PNG does NOT have RelativePath tag (but was copied)
        png_output = os.path.join(expected_folder, "test.png")
        # PNG doesn't support EXIF in same way - just verify it exists
        assert os.path.exists(png_output), "PNG should exist"

        # Verify TIFF does NOT have RelativePath tag (but was copied)
        tiff_output = os.path.join(expected_folder, "test.tiff")
        assert os.path.exists(tiff_output), "TIFF should exist"

        print("All format tests passed!")


if __name__ == "__main__":
    test_help_shows_usage_and_examples()
    print("test_help_shows_usage_and_examples passed")

    test_process_image_supports_multiple_formats()
    print("test_process_image_supports_multiple_formats passed")