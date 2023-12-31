# Sort images based on their capture date into a folder structure <year>/<month>/<day>

## Description

This Python script automatically sorts image files into folders based on their capture dates, creating a structured folder hierarchy in the format `<year>/<month>/<day>`. It reads EXIF data from each image to determine its capture date, rotates the image according to its EXIF orientation, and organizes the images accordingly. This tool is ideal for efficiently managing and organizing large collections of photographs.

## Key Features

- **Date-Based Sorting**: Organizes images into a folder structure of `<year>/<month>/<day>` based on their capture date extracted from EXIF data.
- **Automatic Orientation Correction**: Corrects the orientation of images based on EXIF orientation tags.
- **EXIF Relative Path Tagging**: Adds the relative path as a tag in the image's EXIF data for easy reference and tracking.
- **Concurrent Processing**: Utilizes multi-threading to process multiple images simultaneously, enhancing efficiency.

## Requirements

- Python 3.x
- Pillow (`pip install Pillow`)
- exifread (`pip install exifread`)
- piexif (`pip install piexif`)

## Usage

1. Clone or download the script to your local machine.
2. Install the required dependencies: `Pillow`, `exifread`, and `piexif`.
3. Run the script using the command line:

```
python image_processor.py [basepath] [output_path] [--log LEVEL]
```


- `basepath`: The directory where your images are stored.
- `output_path`: The directory where processed images will be saved.
- `--log`: (Optional) Set the logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Defaults to `INFO`.

## Functions

- `setup_logging(level)`: Configures the logging system.
- `get_exif_orientation(img)`: Retrieves the EXIF orientation of an image.
- `rotate_image_according_to_exif(image_path)`: Rotates an image based on its EXIF orientation.
- `get_date_taken(path)`: Extracts the date the image was taken from its EXIF data.
- `add_relative_path_tag(image_path, relative_path)`: Adds a relative path tag to the image's EXIF data.
- `process_image(file_path, basepath, output_path)`: Processes an individual image file.
- `sort_images(basepath, output_path)`: Sorts and processes all images in a specified directory.
- `main()`: Entry point for the script, handling command line arguments.

## Logging

The script includes detailed logging for tracking its processing steps and handling errors. The logging level can be adjusted via the command line argument `--log`.

## Note

- The script is designed for JPEG images.
- Make sure to back up your images before processing.

## License

This script is released under the [MIT License](https://opensource.org/licenses/MIT).
