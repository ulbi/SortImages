"""String punctuation utilities module."""

import string


def remove_punctuation(text: str) -> str:
    """
    Remove all punctuation characters from the given text.

    Args:
        text: The input string.

    Returns:
        The string with all punctuation removed.
    """
    return text.translate(str.maketrans("", "", string.punctuation))


def count_punctuation(text: str) -> int:
    """
    Count the number of punctuation characters in the given text.

    Args:
        text: The input string.

    Returns:
        The count of punctuation characters.
    """
    return sum(1 for char in text if char in string.punctuation)


def ends_with_punctuation(text: str) -> bool:
    """
    Check if the given text ends with a punctuation character.

    Args:
        text: The input string.

    Returns:
        True if the text ends with punctuation, False otherwise.
    """
    if not text:
        return False
    return text[-1] in string.punctuation