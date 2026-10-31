import unittest
from string_utils import to_upper, to_snake_case


class TestStringUtils(unittest.TestCase):
    """Tests for string_utils module."""

    def test_to_upper_basic(self):
        self.assertEqual(to_upper("hello"), "HELLO")
        self.assertEqual(to_upper("world"), "WORLD")

    def test_to_upper_already_upper(self):
        self.assertEqual(to_upper("HELLO"), "HELLO")

    def test_to_upper_mixed_case(self):
        self.assertEqual(to_upper("HeLlO"), "HELLO")

    def test_to_upper_empty_string(self):
        self.assertEqual(to_upper(""), "")

    def test_to_upper_with_numbers(self):
        self.assertEqual(to_upper("hello123"), "HELLO123")

    def test_to_upper_with_special_chars(self):
        self.assertEqual(to_upper("hello-world"), "HELLO-WORLD")

    def test_to_snake_case_basic(self):
        self.assertEqual(to_snake_case("hello world"), "hello_world")
        self.assertEqual(to_snake_case("Hello World"), "hello_world")

    def test_to_snake_case_camel_case(self):
        self.assertEqual(to_snake_case("helloWorld"), "hello_world")
        self.assertEqual(to_snake_case("HelloWorld"), "hello_world")

    def test_to_snake_case_pascal_case(self):
        self.assertEqual(to_snake_case("HelloWorld"), "hello_world")
        self.assertEqual(to_snake_case("ThisIsATest"), "this_is_a_test")

    def test_to_snake_case_already_snake(self):
        self.assertEqual(to_snake_case("hello_world"), "hello_world")
        self.assertEqual(to_snake_case("already_snake_case"), "already_snake_case")

    def test_to_snake_case_with_numbers(self):
        self.assertEqual(to_snake_case("hello2World"), "hello2_world")
        self.assertEqual(to_snake_case("Version2API"), "version2_api")

    def test_to_snake_case_empty_string(self):
        self.assertEqual(to_snake_case(""), "")

    def test_to_snake_case_single_word(self):
        self.assertEqual(to_snake_case("hello"), "hello")
        self.assertEqual(to_snake_case("Hello"), "hello")

    def test_to_snake_case_multiple_spaces(self):
        self.assertEqual(to_snake_case("hello   world"), "hello_world")

    def test_to_snake_case_leading_trailing_spaces(self):
        self.assertEqual(to_snake_case("  hello world  "), "hello_world")

    def test_to_snake_case_hyphens(self):
        self.assertEqual(to_snake_case("hello-world"), "hello_world")
        self.assertEqual(to_snake_case("hello-world-test"), "hello_world_test")


if __name__ == "__main__":
    unittest.main()