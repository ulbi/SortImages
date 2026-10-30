def reverse_string(s):
    """
    Reverse the given string.

    Args:
        s (str): The string to be reversed.

    Returns:
        str: The reversed string.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected a string, got {type(s).__name__}")
    return s[::-1]