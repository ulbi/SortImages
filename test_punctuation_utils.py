import unittest
from punctuation_utils import remove_punctuation


class TestRemovePunctuation(unittest.TestCase):
    def test_remove_period(self):
        self.assertEqual(remove_punctuation("Hello."), "Hello")

    def test_remove_comma(self):
        self.assertEqual(remove_punctuation("Hello, world"), "Hello world")

    def test_remove_multiple_punctuation(self):
        self.assertEqual(remove_punctuation("Hello, world!"), "Hello world")

    def test_remove_all_punctuation(self):
        self.assertEqual(remove_punctuation("!@#$%^&*()"), "")

    def test_empty_string(self):
        self.assertEqual(remove_punctuation(""), "")

    def test_no_punctuation(self):
        self.assertEqual(remove_punctuation("Hello world"), "Hello world")

    def test_non_string_raises_typeerror(self):
        with self.assertRaises(TypeError):
            remove_punctuation(123)


if __name__ == "__main__":
    unittest.main()