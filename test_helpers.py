import pytest

from helpers import is_supported_image


def test_jpg_is_supported():
    assert is_supported_image("photo.jpg") is True


def test_uppercase_extension_is_supported():
    assert is_supported_image("photo.JPG") is True


def test_jpeg_is_not_supported():
    assert is_supported_image("photo.jpeg") is False


def test_non_image_file_is_not_supported():
    assert is_supported_image("notes.txt") is False


def test_file_without_extension_is_not_supported():
    assert is_supported_image("README") is False


def test_non_string_input_raises():
    with pytest.raises(TypeError):
        is_supported_image(None)
