import string


def remove_punctuation(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return text.translate(str.maketrans("", "", string.punctuation))