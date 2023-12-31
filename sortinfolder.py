import struct
import os
import shutil
import argparse
import logging
from PIL import Image, ExifTags
import exifread
from datetime import datetime
import piexif
import concurrent.futures
import logging

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
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                orientation_value = img._getexif()[orientation]
                logging.debug(f"Found EXIF Orientation: {orientation_value}")
                return orientation_value
        return None
    except (AttributeError, KeyError, IndexError) as e:
        logging.warn(f"No EXIF Orientation tag found. Error: {e}")
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
            # Attempt to load the image to check for truncation
            try:
                img.load()
            except OSError as e:
                logging.error(f"Image file is truncated: {image_path}. Error: {e}")
                return  # Skip processing this image

            orientation = get_exif_orientation(img)
            if orientation == 3:
                img = img.rotate(180, expand=True)
                logging.debug(f"Image rotated 180 degrees: {image_path}")
            elif orientation == 6:
                img = img.rotate(270, expand=True)
                logging.debug(f"Image rotated 270 degrees: {image_path}")
            elif orientation == 8:
                img = img.rotate(90, expand=True)
                logging.debug(f"Image rotated 90 degrees: {image_path}")
            else:
                logging.debug(f"No rotation required for image: {image_path}")

            if orientation in [3, 6, 8]:
                img.save(image_path)
    except Exception as e:
        logging.error(f"Error in rotating image {image_path}: {e}")

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
                logging.debug(f"Extracted date from EXIF data: {date_str}")
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            else:
                raise KeyError
    except Exception:
        ctime = datetime.fromtimestamp(os.path.getctime(path))
        logging.warning(f"EXIF DateTimeOriginal not found in {path}. Using file creation date: {ctime}")
        return ctime

def add_relative_path_tag(image_path, relative_path):
    """
    Adds a relative path tag to the EXIF UserComment of a JPEG image.

    Args:
        image_path (str): The path to the JPEG image file.
        relative_path (str): The relative path to be added as a tag.

    Raises:
        Exception: If an error occurs while adding the tag.

    """
    try:
        if image_path.lower().endswith('.jpg'):
            exif_dict = piexif.load(image_path)
            user_comment = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b'')
            new_comment = user_comment + b"\nRelativePath:" + relative_path.encode()
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = new_comment

            try:
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, image_path)
                logging.debug(f"Added original relative path to EXIF UserComment in {image_path}")
            except struct.error as e:
                logging.error(f"Struct error while processing EXIF data in {image_path}: {e}")
        else:
            logging.info(f"File format not supported for tagging: {image_path}")
    except Exception as e:
        logging.error(f"Error adding tag to file {image_path}: {e}")

def process_image(file_path, basepath, output_path):
    """
    Process an image file by copying it to a new location, organizing it by date, rotating it if needed,
    and adding a tag with the relative path.

    Args:
        file_path (str): The path of the image file to be processed.
        basepath (str): The base path of the directory containing the image file.
        output_path (str): The path of the directory where the processed image will be saved.

    Returns:
        None
    """
    if file_path.lower().endswith('.jpg') and os.path.getsize(file_path) > 100 * 1024:
        logging.debug(f"Processing file: {file_path}")
        date_taken = get_date_taken(file_path)
        new_folder = os.path.join(output_path, date_taken.strftime("%Y/%m/%d"))
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
            logging.info(f"Created directory for date: {new_folder}")

        new_file_path = os.path.join(new_folder, os.path.basename(file_path))
        
        # Copying the image
        shutil.copy2(file_path, new_file_path)
        logging.info(f"Copied {file_path} to {new_file_path}")

        # Rotate image if needed
        rotate_image_according_to_exif(new_file_path)

        # Add the relative path as a tag
        relative_path = os.path.relpath(os.path.dirname(file_path), basepath)
        add_relative_path_tag(new_file_path, relative_path)

def sort_images(basepath, output_path):
    """
    Sorts images in the specified basepath and saves them to the output_path.
    This is done in 30 threads in parallel.

    Args:
        basepath (str): The base path where the images are located.
        output_path (str): The path where the sorted images will be saved.

    Returns:
        None
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        logging.info(f"Created output directory: {output_path}")

    # List all files to process
    files_to_process = []
    for root, dirs, files in os.walk(basepath):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    # Process files in parallel using a ThreadPool
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_image, file_path, basepath, output_path) for file_path in files_to_process]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # to catch exceptions

def main():
    """
    Sort and copy images based on date, with automatic rotation and tagging.

    Args:
        basepath (str): The base path where the images are located.
        output_path (str): The output path where images will be copied to.
        log (str, optional): Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to "INFO".
    """
    parser = argparse.ArgumentParser(description="Sort and copy images based on date, with automatic rotation and tagging.")
    parser.add_argument("basepath", type=str, help="The base path where the images are located.")
    parser.add_argument("output_path", type=str, help="The output path where images will be copied to.")
    parser.add_argument("--log", type=str, default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    # Set up logging level based on the argument
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log}")
    setup_logging(numeric_level)

    logging.info(f"Script arguments - Basepath: {args.basepath}, Output Path: {args.output_path}")
    
    sort_images(args.basepath, args.output_path)

if __name__ == "__main__":
    main()
