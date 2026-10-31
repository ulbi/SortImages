"""
String utilities module providing common string transformations.
"""

import re


def to_upper(text: str) -> str:
    """
    Convert a string to uppercase.

    Args:
        text: The input string to convert.

    Returns:
        The uppercase version of the input string.
    """
    return text.upper()


def to_snake_case(text: str) -> str:
    """
    Convert a string to snake_case.

    Handles various input formats:
    - Space-separated words: "hello world" -> "hello_world"
    - CamelCase: "helloWorld" -> "hello_world"
    - PascalCase: "HelloWorld" -> "hello_world"
    - Hyphenated: "hello-world" -> "hello_world"
    - Already snake_case: "hello_world" -> "hello_world"

    Args:
        text: The input string to convert.

    Returns:
        The snake_case version of the input string.
    """
    if not text:
        return ""

    # Replace hyphens and spaces with underscores
    text = re.sub(r'[-\s]+', '_', text.strip())

    # Handle camelCase and PascalCase: insert underscore before uppercase letters
    # that follow a lowercase letter or digit
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)

    # Handle consecutive uppercase followed by lowercase (e.g., "ATest" -> "A_Test")
    text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', text)

    # Convert to lowercase
    text = text.lower()

    # Collapse multiple underscores into one
    text = re.sub(r'_+', '_', text)

    # Remove leading/trailing underscores
    text = text.strip('_')

    return text