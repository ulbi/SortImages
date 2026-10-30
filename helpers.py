"""Small helpers shared by the image sorting script."""


def is_supported_image(filename):
    """
    Check whether a filename refers to a supported image file.

    Only JPEG files (`.jpg`/`.JPG`) are supported by the sorting script.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the filename ends with the `.jpg` extension, False otherwise.

    Raises:
        TypeError: If filename is not a string.
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    return filename.lower().endswith(".jpg")
