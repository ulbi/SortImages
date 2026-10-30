import unittest


class TestToUpper(unittest.TestCase):
    def test_basic(self):
        from case_utils import to_upper
        self.assertEqual(to_upper("hello"), "HELLO")

    def test_with_numbers_and_symbols(self):
        from case_utils import to_upper
        self.assertEqual(to_upper("hello 123!"), "HELLO 123!")

    def test_unicode(self):
        from case_utils import to_upper
        self.assertEqual(to_upper("héllo wörld"), "HÉLLO WÖRLD")

    def test_empty_string(self):
        from case_utils import to_upper
        self.assertEqual(to_upper(""), "")

    def test_non_string_raises_type_error(self):
        from case_utils import to_upper
        with self.assertRaises(TypeError):
            to_upper(123)
        with self.assertRaises(TypeError):
            to_upper(None)


class TestToSnakeCase(unittest.TestCase):
    def test_camel_case_boundary(self):
        from case_utils import to_snake_case
        self.assertEqual(to_snake_case("HelloWorld"), "hello_world")

    def test_spaces_to_underscore(self):
        from case_utils import to_snake_case
        self.assertEqual(to_snake_case("foo bar"), "foo_bar")

    def test_delimiters_collapse_to_single_underscore(self):
        from case_utils import to_snake_case
        self.assertEqual(to_snake_case("Foo-Bar Baz!"), "foo_bar_baz")

    def test_idempotent(self):
        from case_utils import to_snake_case
        self.assertEqual(to_snake_case("already_snake_case"), "already_snake_case")

    def test_empty_string(self):
        from case_utils import to_snake_case
        self.assertEqual(to_snake_case(""), "")

    def test_non_string_raises_type_error(self):
        from case_utils import to_snake_case
        with self.assertRaises(TypeError):
            to_snake_case(None)


if __name__ == "__main__":
    unittest.main()