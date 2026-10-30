"""String case utilities."""


def to_upper(s: str) -> str:
    """Convert string to uppercase."""
    if not isinstance(s, str):
        raise TypeError(f"Expected str, got {type(s).__name__}")
    return s.upper()


def to_snake_case(s: str) -> str:
    """Convert string to snake_case."""
    if not isinstance(s, str):
        raise TypeError(f"Expected str, got {type(s).__name__}")
    if not s:
        return ""

    result = []
    prev_was_underscore = False

    for i, ch in enumerate(s):
        if ch.isupper():
            if i > 0 and not prev_was_underscore:
                result.append("_")
            result.append(ch.lower())
            prev_was_underscore = False
        elif ch.islower() or ch.isdigit():
            result.append(ch)
            prev_was_underscore = False
        else:
            if not prev_was_underscore and result:
                result.append("_")
                prev_was_underscore = True

    return "".join(result).strip("_")


if __name__ == "__main__":
    import sys

    print("Testing to_upper:")
    print(f"  to_upper('hello') = {to_upper('hello')}")
    print(f"  to_upper('hello 123!') = {to_upper('hello 123!')}")
    print(f"  to_upper('héllo wörld') = {to_upper('héllo wörld')}")
    print(f"  to_upper('') = '{to_upper('')}'")

    print("\nTesting to_snake_case:")
    print(f"  to_snake_case('HelloWorld') = {to_snake_case('HelloWorld')}")
    print(f"  to_snake_case('foo bar') = {to_snake_case('foo bar')}")
    print(f"  to_snake_case('Foo-Bar Baz!') = {to_snake_case('Foo-Bar Baz!')}")
    print(f"  to_snake_case('already_snake_case') = {to_snake_case('already_snake_case')}")
    print(f"  to_snake_case('') = '{to_snake_case('')}'")

    print("\nTesting TypeError:")
    try:
        to_upper(123)
    except TypeError as e:
        print(f"  to_upper(123) -> TypeError: {e}")
    try:
        to_snake_case(None)
    except TypeError as e:
        print(f"  to_snake_case(None) -> TypeError: {e}")