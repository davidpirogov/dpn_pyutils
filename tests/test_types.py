import unittest

from dpn_pyutils.types import (
    FALSE_BOOLS,
    TRUE_BOOLS,
    is_boolean,
    is_integer,
    is_numeric,
    parse_type,
)


class TestTypes(unittest.TestCase):
    """
    Tests for the types module utility functions.
    """

    def test_is_numeric_valid_integers(self):
        """Test is_numeric with valid integer strings."""
        valid_integers = [
            "0",
            "1",
            "123",
            "-123",
            "+123",
            "0",
            "-0",
            "+0",
        ]

        for num_str in valid_integers:
            with self.subTest(num_str=num_str):
                self.assertTrue(is_numeric(num_str), f"'{num_str}' should be numeric")

    def test_is_numeric_valid_floats(self):
        """Test is_numeric with valid float strings."""
        valid_floats = [
            "0.0",
            "1.0",
            "123.45",
            "-123.45",
            "+123.45",
            ".5",
            "0.5",
            "1e2",
            "1E2",
            "1.23e10",
            "1.23E-10",
            "-1.23e-10",
            "+1.23e+10",
        ]

        for num_str in valid_floats:
            with self.subTest(num_str=num_str):
                self.assertTrue(is_numeric(num_str), f"'{num_str}' should be numeric")

    def test_is_numeric_special_values(self):
        """Test is_numeric with special numeric values."""
        special_values = [
            "inf",
            "nan",
            "-inf",
            "+inf",
        ]

        for num_str in special_values:
            with self.subTest(num_str=num_str):
                self.assertTrue(is_numeric(num_str), f"'{num_str}' should be numeric")

    def test_is_numeric_invalid_strings(self):
        """Test is_numeric with invalid non-numeric strings."""
        invalid_strings = [
            "",
            "abc",
            "hello",
            "123abc",
            "abc123",
            "12.34.56",
            "++123",
            "--123",
            "1.2.3",
            "e123",
            "E123",
            "1e",
            "1E",
            "1e+",
            "1E-",
            "None",
            "True",
            "False",
        ]

        for num_str in invalid_strings:
            with self.subTest(num_str=num_str):
                self.assertFalse(is_numeric(num_str), f"'{num_str}' should not be numeric")

    def test_is_numeric_edge_cases(self):
        """Test is_numeric with edge cases."""
        # Test with whitespace (should work - Python's float() handles whitespace)
        self.assertTrue(is_numeric(" 123 "))
        self.assertTrue(is_numeric("123 "))
        self.assertTrue(is_numeric(" 123"))

        # Test with None (should return False)
        self.assertFalse(is_numeric(None))

        # Test with non-string types (should return True for numeric types)
        self.assertTrue(is_numeric(123))
        self.assertTrue(is_numeric(123.45))
        self.assertTrue(is_numeric(True))  # True is 1
        self.assertTrue(is_numeric(False))  # False is 0

    def test_is_integer_valid_integers(self):
        """Test is_integer with valid integer strings."""
        valid_integers = [
            "0",
            "1",
            "123",
            "-123",
            "+123",
            "0.0",
            "1.0",
            "123.0",
            "-123.0",
            "+123.0",
            "1e2",  # 100.0
            "1E2",  # 100.0
            "1.23e2",  # 123.0
            "2e0",  # 2.0
        ]

        for num_str in valid_integers:
            with self.subTest(num_str=num_str):
                self.assertTrue(is_integer(num_str), f"'{num_str}' should be an integer")

    def test_is_integer_invalid_floats(self):
        """Test is_integer with non-integer numeric strings."""
        invalid_integers = [
            "0.1",
            "1.5",
            "123.45",
            "-123.45",
            "+123.45",
            ".5",
            "0.5",
            "1.23e1",  # 12.3
            "1.23E-1",  # 0.123
        ]

        for num_str in invalid_integers:
            with self.subTest(num_str=num_str):
                self.assertFalse(is_integer(num_str), f"'{num_str}' should not be an integer")

    def test_is_integer_non_numeric(self):
        """Test is_integer with non-numeric strings."""
        non_numeric = [
            "",
            "abc",
            "hello",
            "123abc",
            "abc123",
            "true",
            "false",
            "yes",
            "no",
        ]

        for num_str in non_numeric:
            with self.subTest(num_str=num_str):
                self.assertFalse(is_integer(num_str), f"'{num_str}' should not be an integer")

    def test_is_integer_edge_cases(self):
        """Test is_integer with edge cases."""
        # Test with None (should return False)
        self.assertFalse(is_integer(None))

        # Test with non-string types
        self.assertTrue(is_integer(123))  # Integer is integer
        self.assertFalse(is_integer(123.45))  # Float is not integer
        self.assertTrue(is_integer(True))  # True is 1 (integer)
        self.assertTrue(is_integer(False))  # False is 0 (integer)

    def test_is_boolean_valid_true_values(self):
        """Test is_boolean with valid true boolean strings."""
        true_values = [
            "true",
            "TRUE",
            "True",
            "TrUe",
            "yes",
            "YES",
            "Yes",
            "YeS",
            "1",
        ]

        for bool_str in true_values:
            with self.subTest(bool_str=bool_str):
                self.assertTrue(is_boolean(bool_str), f"'{bool_str}' should be a boolean")

    def test_is_boolean_valid_false_values(self):
        """Test is_boolean with valid false boolean strings."""
        false_values = [
            "false",
            "FALSE",
            "False",
            "FaLsE",
            "no",
            "NO",
            "No",
            "nO",
            "0",
        ]

        for bool_str in false_values:
            with self.subTest(bool_str=bool_str):
                self.assertTrue(is_boolean(bool_str), f"'{bool_str}' should be a boolean")

    def test_is_boolean_invalid_values(self):
        """Test is_boolean with invalid boolean strings."""
        invalid_values = [
            "",
            "maybe",
            "2",
            "10",
            "on",
            "off",
            "enabled",
            "disabled",
            "y",
            "n",
            "t",
            "f",
            "yesno",
            "truely",
            "falsely",
            "1.0",
            "0.0",
            "123",
            "abc",
        ]

        for bool_str in invalid_values:
            with self.subTest(bool_str=bool_str):
                self.assertFalse(is_boolean(bool_str), f"'{bool_str}' should not be a boolean")

    def test_is_boolean_edge_cases(self):
        """Test is_boolean with edge cases."""
        # Test with None (should return False)
        self.assertFalse(is_boolean(None))

        # Test with non-string types (should return False)
        self.assertFalse(is_boolean(True))
        self.assertFalse(is_boolean(False))
        self.assertFalse(is_boolean(1))
        self.assertFalse(is_boolean(0))

    def test_parse_type_integers(self):
        """Test parse_type with integer strings."""
        test_cases = [
            ("0", 0),
            ("1", 1),
            ("123", 123),
            ("-123", -123),
            ("+123", 123),
            ("0.0", 0),
            ("1.0", 1),
            ("123.0", 123),
            ("-123.0", -123),
            ("+123.0", 123),
            ("1e2", 100),  # 100.0 -> 100
            ("1E2", 100),  # 100.0 -> 100
            ("1.23e2", 123),  # 123.0 -> 123
            ("2e0", 2),  # 2.0 -> 2
        ]

        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str, expected=expected):
                result = parse_type(input_str)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)

    def test_parse_type_floats(self):
        """Test parse_type with float strings."""
        test_cases = [
            ("0.1", 0.1),
            ("1.5", 1.5),
            ("123.45", 123.45),
            ("-123.45", -123.45),
            ("+123.45", 123.45),
            (".5", 0.5),
            ("0.5", 0.5),
            ("1.23e1", 12.3),  # 12.3
            ("1.23E-1", 0.123),  # 0.123
        ]

        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str, expected=expected):
                result = parse_type(input_str)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, float)

    def test_parse_type_booleans(self):
        """Test parse_type with boolean strings."""
        # True values
        true_cases = [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("TrUe", True),
            ("yes", True),
            ("YES", True),
            ("Yes", True),
            ("YeS", True),
        ]

        for input_str, expected in true_cases:
            with self.subTest(input_str=input_str, expected=expected):
                result = parse_type(input_str)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, bool)

        # False values
        false_cases = [
            ("false", False),
            ("FALSE", False),
            ("False", False),
            ("FaLsE", False),
            ("no", False),
            ("NO", False),
            ("No", False),
            ("nO", False),
        ]

        for input_str, expected in false_cases:
            with self.subTest(input_str=input_str, expected=expected):
                result = parse_type(input_str)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, bool)

    def test_parse_type_strings(self):
        """Test parse_type with non-numeric, non-boolean strings."""
        test_cases = [
            "hello",
            "world",
            "maybe",
            "on",
            "off",
            "enabled",
            "disabled",
            "y",
            "n",
            "t",
            "f",
            "yesno",
            "truely",
            "falsely",
            "123abc",
            "abc123",
            "12.34.56",
            "++123",
            "--123",
            "1.2.3",
            "e123",
            "E123",
            "1e",
            "1E",
            "1e+",
            "1E-",
            "None",
        ]

        for input_str in test_cases:
            with self.subTest(input_str=input_str):
                result = parse_type(input_str)
                self.assertEqual(result, input_str)
                self.assertIsInstance(result, str)

    def test_parse_type_edge_cases(self):
        """Test parse_type with edge cases."""
        # Test with None (should return None)
        self.assertIsNone(parse_type(None))

        # Test with non-string types (should return the value as-is)
        self.assertEqual(parse_type(123), 123)
        self.assertEqual(parse_type(123.45), 123.45)
        self.assertEqual(parse_type(True), True)
        self.assertEqual(parse_type(False), False)

    def test_constants_defined(self):
        """Test that the boolean constants are properly defined."""
        self.assertIsInstance(TRUE_BOOLS, list)
        self.assertIsInstance(FALSE_BOOLS, list)

        # Check that constants contain expected values
        expected_true = ["true", "yes", "1"]
        expected_false = ["false", "no", "0"]

        self.assertEqual(set(TRUE_BOOLS), set(expected_true))
        self.assertEqual(set(FALSE_BOOLS), set(expected_false))

        # Check that constants are used in the functions
        for true_val in TRUE_BOOLS:
            self.assertTrue(is_boolean(true_val))
            self.assertEqual(parse_type(true_val), True)

        for false_val in FALSE_BOOLS:
            self.assertTrue(is_boolean(false_val))
            self.assertEqual(parse_type(false_val), False)

    def test_parse_type_priority_order(self):
        """Test that parse_type follows the correct priority order."""
        # Test priority: integer > float > boolean > empty string > string

        # Integer should take priority over boolean
        self.assertEqual(parse_type("1"), 1)  # Not True
        self.assertEqual(parse_type("0"), 0)  # Not False

        # Integer should take priority over float for whole numbers
        self.assertEqual(parse_type("1.0"), 1)  # Integer, not float
        self.assertEqual(parse_type("0.1"), 0.1)  # Float

        # Boolean should take priority over string
        self.assertEqual(parse_type("true"), True)  # Not "true"
        self.assertEqual(parse_type("false"), False)  # Not "false"

        # Empty string should return None
        self.assertIsNone(parse_type(""))

        # String should be last priority
        self.assertEqual(parse_type("maybe"), "maybe")
        self.assertEqual(parse_type("2"), 2)  # Integer 2, not string "2"

    def test_comprehensive_integration(self):
        """Test comprehensive integration of all functions."""
        test_data = [
            # (input, is_numeric, is_integer, is_boolean, parse_type_result, parse_type_type)
            ("123", True, True, False, 123, int),
            ("123.45", True, False, False, 123.45, float),
            ("123.0", True, True, False, 123, int),  # Integer, not float
            ("true", False, False, True, True, bool),
            ("false", False, False, True, False, bool),
            ("yes", False, False, True, True, bool),
            ("no", False, False, True, False, bool),
            ("1", True, True, True, 1, int),  # Integer takes priority
            ("0", True, True, True, 0, int),  # Integer takes priority
            ("", False, False, False, None, type(None)),
            ("hello", False, False, False, "hello", str),
            ("maybe", False, False, False, "maybe", str),
            ("1e2", True, True, False, 100, int),  # Integer, not float
            ("1.23e1", True, False, False, 12.3, float),
        ]

        for (
            input_str,
            expected_numeric,
            expected_integer,
            expected_boolean,
            expected_parse,
            expected_type,
        ) in test_data:
            with self.subTest(input_str=input_str):
                self.assertEqual(is_numeric(input_str), expected_numeric, f"is_numeric('{input_str}')")
                self.assertEqual(is_integer(input_str), expected_integer, f"is_integer('{input_str}')")
                self.assertEqual(is_boolean(input_str), expected_boolean, f"is_boolean('{input_str}')")

                result = parse_type(input_str)
                self.assertEqual(result, expected_parse, f"parse_type('{input_str}')")
                self.assertIsInstance(result, expected_type, f"parse_type('{input_str}') type")

    def test_parse_type_missing_branch_coverage(self):
        """Test parse_type to cover missing branch coverage (line 197->202)."""
        # This test covers the missing branch in parse_type where
        # the function returns the original string when it's not numeric,
        # not boolean, and not empty
        test_cases = [
            "hello",
            "world",
            "maybe",
            "on",
            "off",
            "enabled",
            "disabled",
            "y",
            "n",
            "t",
            "f",
            "yesno",
            "truely",
            "falsely",
            "123abc",
            "abc123",
            "12.34.56",
            "++123",
            "--123",
            "1.2.3",
            "e123",
            "E123",
            "1e",
            "1E",
            "1e+",
            "1E-",
            "None",
        ]

        for input_str in test_cases:
            with self.subTest(input_str=input_str):
                result = parse_type(input_str)
                self.assertEqual(result, input_str)
                self.assertIsInstance(result, str)

    def test_parse_type_edge_case_branch_coverage(self):
        """Test parse_type edge case to ensure complete branch coverage."""
        # Test the specific branch that was missing coverage
        # This covers the case where the string is not numeric, not boolean, and not empty
        # so it falls through to the final return statement

        # Test with a string that's clearly not numeric, boolean, or empty
        result = parse_type("definitely_not_numeric_or_boolean")
        self.assertEqual(result, "definitely_not_numeric_or_boolean")
        self.assertIsInstance(result, str)

        # Test with a string that contains special characters
        result = parse_type("test@example.com")
        self.assertEqual(result, "test@example.com")
        self.assertIsInstance(result, str)

        # Test with a string that looks like a boolean but isn't
        result = parse_type("maybe")
        self.assertEqual(result, "maybe")
        self.assertIsInstance(result, str)

        # Test with a string that looks like a number but isn't
        result = parse_type("123abc")
        self.assertEqual(result, "123abc")
        self.assertIsInstance(result, str)

    def test_parse_type_false_boolean_branch(self):
        """Test parse_type with false boolean values to cover the missing branch."""
        # Test the specific branch 197->202 which is the elif n.lower() in FALSE_BOOLS
        # Only test string values that are not numeric (since "0" would be caught by is_numeric first)
        false_values = ["false", "FALSE", "False", "no", "NO", "No"]

        for false_val in false_values:
            with self.subTest(value=false_val):
                result = parse_type(false_val)
                self.assertEqual(result, False)
                self.assertIsInstance(result, bool)

    def test_parse_type_false_boolean_branch_coverage(self):
        """Test parse_type false boolean branch to ensure complete coverage."""
        # This test specifically targets the missing branch 197->202
        # We need to ensure the elif condition is reached

        # Test with "false" - this should trigger the elif branch
        result = parse_type("false")
        self.assertEqual(result, False)
        self.assertIsInstance(result, bool)

        # Test with "no" - this should also trigger the elif branch
        result = parse_type("no")
        self.assertEqual(result, False)
        self.assertIsInstance(result, bool)

        # Verify that these are actually boolean values, not strings
        self.assertNotEqual(result, "no")
        self.assertNotEqual(result, "false")

    def test_parse_type_false_boolean_comprehensive(self):
        """Test parse_type with all false boolean values to ensure complete branch coverage."""
        # Test all false boolean values to ensure the elif branch 197->202 is covered
        false_values = ["false", "FALSE", "False", "no", "NO", "No"]

        for false_val in false_values:
            with self.subTest(value=false_val):
                result = parse_type(false_val)
                self.assertEqual(result, False)
                self.assertIsInstance(result, bool)
                # Ensure it's not returning the string
                self.assertNotEqual(result, false_val)

    def test_parse_type_empty_string(self):
        """Test parse_type with empty string to ensure complete coverage."""
        # Test empty string - this should trigger the elif n == "" branch
        result = parse_type("")
        self.assertIsNone(result)

        # Test that it's actually None, not an empty string
        self.assertNotEqual(result, "")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
