import argparse
import concurrent.futures
import logging
import os
import shutil
import struct
import sys
from datetime import datetime

import exifread
import piexif
from PIL import ExifTags, Image, UnidentifiedImageError

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.heic', '.tiff', '.tif', '.bmp', '.webp'}

logger = logging.getLogger(__name__)

def setup_logging(level):
    """
    Set up logging configuration.

    Args:
        level (int): The logging level to be set.

    Returns:
        None
    """
    log_format = '%(asctime)s - [Thread %(thread)d] - %(levelname)s - %(message)s'
    logging.basicConfig(level=level, format=log_format)

def get_exif_orientation(img):
    """
    Get the EXIF orientation value from the given image.

    Args:
        img: The image object.

    Returns:
        The EXIF orientation value if found, None otherwise.
    """
    try:
        exif = img._getexif()
        if exif is None:
            return None
        for orientation in ExifTags.TAGS:
            if ExifTags.TAGS[orientation] == 'Orientation':
                orientation_value = exif[orientation]
                logger.debug(f"Found EXIF Orientation: {orientation_value}")
                return orientation_value
        return None
    except (AttributeError, KeyError, IndexError, TypeError) as e:
        logger.debug(f"No EXIF Orientation tag found. Error: {e}")
        return None

def rotate_image_according_to_exif(image_path):
    """
    Rotates the image based on the EXIF orientation tag.
    And saves the image back to the same file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        None
    """
    try:
        with Image.open(image_path) as img:
            try:
                img.load()
            except OSError as e:
                logger.error(f"Image file is truncated: {image_path}. Error: {e}")
                return

            orientation = get_exif_orientation(img)
            if orientation == 3:
                img = img.rotate(180, expand=True)
                logger.debug(f"Image rotated 180 degrees: {image_path}")
            elif orientation == 6:
                img = img.rotate(270, expand=True)
                logger.debug(f"Image rotated 270 degrees: {image_path}")
            elif orientation == 8:
                img = img.rotate(90, expand=True)
                logger.debug(f"Image rotated 90 degrees: {image_path}")
            else:
                logger.debug(f"No rotation required for image: {image_path}")

            if orientation in [3, 6, 8]:
                img.save(image_path)
    except OSError:
        raise
    except (UnidentifiedImageError, struct.error) as e:
        logger.error(f"Error in rotating image {image_path}: {e}")
        raise

def get_date_taken(path):
    """
    Retrieves the date taken from the EXIF data of an image file.
    If the EXIF DateTimeOriginal tag is present, it is used.
    Otherwise, the file creation date is used as a fallback.

    Args:
        path (str): The path to the image file.

    Returns:
        datetime.datetime: The date taken of the image.

    Raises:
        KeyError: If the EXIF DateTimeOriginal tag is not found.
    """
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")
            if "EXIF DateTimeOriginal" in tags:
                date_str = str(tags["EXIF DateTimeOriginal"])
                logger.debug(f"Extracted date from EXIF data: {date_str}")
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            else:
                raise KeyError
    except (OSError, KeyError, ValueError):
        ctime = datetime.fromtimestamp(os.path.getctime(path))
        logger.warning(f"EXIF DateTimeOriginal not found in {path}. Using file creation date: {ctime}")
        return ctime

def add_relative_path_tag(image_path, relative_path):
    """
    Adds a relative path tag to the EXIF UserComment of a JPEG image.

    Args:
        image_path (str): The path to the JPEG image file.
        relative_path (str): The relative path to be added as a tag.

    Raises:
        OSError: If an error occurs while adding the tag.
    """
    try:
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            exif_dict = piexif.load(image_path)
            user_comment = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b'')
            new_comment = user_comment + b"\nRelativePath:" + relative_path.encode()
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = new_comment

            try:
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, image_path)
                logger.debug(f"Added original relative path to EXIF UserComment in {image_path}")
            except struct.error as e:
                logger.error(f"Struct error while processing EXIF data in {image_path}: {e}")
                raise
        else:
            logger.info(f"File format not supported for tagging: {image_path}")
    except (OSError, piexif.InvalidImageDataError) as e:
        logger.error(f"Error adding tag to file {image_path}: {e}")
        raise

def process_image(file_path, basepath, output_path, dry_run=False):
    """
    Process an image file by copying it to a new location, organizing it by date, rotating it if needed,
    and adding a tag with the relative path.

    Args:
        file_path (str): The path of the image file to be processed.
        basepath (str): The base path of the directory containing the image file.
        output_path (str): The path of the directory where the processed image will be saved.
        dry_run (bool): If True, simulate processing without copying files. Default: False.

    Returns:
        None
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        logger.debug(f"Skipping unsupported format: {file_path}")
        return

    logger.debug(f"Processing file: {file_path}")
    date_taken = get_date_taken(file_path)
    new_folder = os.path.join(output_path, date_taken.strftime("%Y/%m/%d"))
    if not dry_run and not os.path.exists(new_folder):
        os.makedirs(new_folder)
        logger.info(f"Created directory for date: {new_folder}")

    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    new_file_path = os.path.join(new_folder, base_name)

    counter = 1
    while os.path.exists(new_file_path):
        new_name = f"{name}_{counter}{ext}"
        new_file_path = os.path.join(new_folder, new_name)
        counter += 1

    if counter > 1:
        logger.info(f"Filename collision detected for {base_name}, using {os.path.basename(new_file_path)}")

    if dry_run:
        logger.info(f"DRY RUN: Would copy {file_path} to {new_file_path}")
        try:
            with Image.open(file_path) as img:
                orientation = get_exif_orientation(img)
                if orientation in [3, 6, 8]:
                    angle = {3: 180, 6: 270, 8: 90}[orientation]
                    logger.info(f"DRY RUN: Would rotate image {new_file_path} by {angle} degrees")
                else:
                    logger.info(f"DRY RUN: No rotation needed for {new_file_path}")
        except (OSError, UnidentifiedImageError) as e:
            logger.warning(f"DRY RUN: Could not check rotation for {file_path}: {e}")
        ext_check = os.path.splitext(new_file_path)[1].lower()
        if ext_check in ('.jpg', '.jpeg'):
            relative_path = os.path.relpath(os.path.dirname(file_path), basepath)
            logger.info(f"DRY RUN: Would add RelativePath tag: RelativePath:{relative_path} to {new_file_path}")
        else:
            logger.info(f"DRY RUN: Would skip tag for {new_file_path} (format not supported for tagging)")
        return

    shutil.copy2(file_path, new_file_path)
    logger.info(f"Copied {file_path} to {new_file_path}")

    rotate_image_according_to_exif(new_file_path)

    relative_path = os.path.relpath(os.path.dirname(file_path), basepath)
    add_relative_path_tag(new_file_path, relative_path)

def sort_images(basepath, output_path, threads=30, dry_run=False):
    """
    Sorts images in the specified basepath and saves them to the output_path.

    Args:
        basepath (str): The base path where the images are located.
        output_path (str): The path where the sorted images will be saved.
        threads (int): Number of worker threads (1-100). Default: 30.
        dry_run (bool): If True, simulate processing without copying files. Default: False.

    Returns:
        tuple: (success_count, failure_count, errors_list)
    """
    if not 1 <= threads <= 100:
        raise ValueError(f"threads must be between 1 and 100, got {threads}")

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        logger.info(f"Created output directory: {output_path}")

    if dry_run:
        logger.info("DRY RUN MODE - Simulating processing without copying files")

    files_to_process = []
    for root, dirs, files in os.walk(basepath):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    success_count = 0
    failure_count = 0
    errors_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(process_image, file_path, basepath, output_path, dry_run): file_path for file_path in files_to_process}
        for future in concurrent.futures.as_completed(futures):
            file_path = futures[future]
            try:
                future.result()
                success_count += 1
            except Exception as e:  # noqa: BLE001 - Catch all exceptions from worker threads to collect errors
                failure_count += 1
                error_info = {
                    "file": file_path,
                    "type": type(e).__name__,
                    "message": str(e)
                }
                errors_list.append(error_info)
                logger.error(f"Failed to process {file_path}: {type(e).__name__}: {e}")

    total_processed = success_count + failure_count
    logger.info(f"Processed: {total_processed}, Succeeded: {success_count}, Failed: {failure_count}")

    return success_count, failure_count, errors_list

def main():
    """
    Sort and copy images based on date, with automatic rotation and tagging.

    Args:
        basepath (str): The base path where the images are located.
        output_path (str): The output path where images will be copied to.
        log (str, optional): Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to "INFO".
    """
    epilog = """Examples:
  sortimages /data/photos /data/sorted
  sortimages /data/photos /data/sorted --log DEBUG
  sortimages /data/photos /data/sorted --threads 5 --dry-run
"""
    parser = argparse.ArgumentParser(
        prog="sortimages",
        description="Sort and copy images based on date, with automatic rotation and tagging.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("basepath", type=str, help="The base path where the images are located.")
    parser.add_argument("output_path", type=str, help="The output path where images will be copied to.")
    parser.add_argument("--log", type=str, default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--threads", type=int, default=30, help="Number of worker threads (1-100). Default: 30")
    parser.add_argument("--dry-run", action="store_true", help="Simulate processing without copying files")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise TypeError(f"Invalid log level: {args.log}")
    setup_logging(numeric_level)

    logger.info(f"Script arguments - Basepath: {args.basepath}, Output Path: {args.output_path}, Threads: {args.threads}, Dry-run: {args.dry_run}")

    _success_count, failure_count, _errors_list = sort_images(args.basepath, args.output_path, threads=args.threads, dry_run=args.dry_run)

    if failure_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
