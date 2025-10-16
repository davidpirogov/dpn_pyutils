import unittest

from dpn_pyutils.money import format_currency_market_display_float


class TestCurrencyFormatting(unittest.TestCase):
    """
    Tests for the format_currency_market_display_float function.

    This function formats currency values according to market display conventions
    with different formatting rules based on value magnitude.
    """

    def test_micro_values_positive(self):
        """Test formatting of very small positive values (< $0.000001)."""
        test_cases = [
            (0.0000005, "<$0.000001"),
            (0.0000001, "<$0.000001"),
            (0.00000001, "<$0.000001"),
            (0.000000001, "<$0.000001"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_micro_values_negative(self):
        """Test formatting of very small negative values (< -$0.000001)."""
        test_cases = [
            (-0.0000005, "<-$0.000001"),
            (-0.0000001, "<-$0.000001"),
            (-0.00000001, "<-$0.000001"),
            (-0.000000001, "<-$0.000001"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_small_fractions_high_precision(self):
        """Test formatting of small fractions with high precision (6 decimal places)."""
        test_cases = [
            (0.000001, "<$0.000001"),
            (0.000005, "$0.000005"),
            (0.000010, "$0.00001"),
            (0.000100, "$0.0001"),
            (0.000999, "$0.000999"),
            (0.002895, "$0.002895"),
            (0.000690, "$0.00069"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_small_fractions_negative(self):
        """Test formatting of small negative fractions."""
        test_cases = [
            (-0.000001, "<-$0.000001"),
            (-0.000005, "-$0.000005"),
            (-0.000100, "-$0.0001"),
            (-0.002895, "-$0.002895"),
            (-0.000690, "-$0.00069"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_cents_range(self):
        """Test formatting of cent values ($0.01 - $0.99)."""
        test_cases = [
            (0.01, "$0.01"),
            (0.25, "$0.25"),
            (0.50, "$0.50"),
            (0.99, "$0.99"),
            (0.10, "$0.10"),
            (0.05, "$0.05"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_cents_range_negative(self):
        """Test formatting of negative cent values."""
        test_cases = [
            (-0.01, "-$0.01"),
            (-0.25, "-$0.25"),
            (-0.50, "-$0.50"),
            (-0.99, "-$0.99"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_dollar_range(self):
        """Test formatting of dollar values ($1.00 - $999.99)."""
        test_cases = [
            (1.00, "$1.00"),
            (1.23, "$1.23"),
            (10.50, "$10.50"),
            (100.00, "$100.00"),
            (999.99, "$999.99"),
            (123.45, "$123.45"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_dollar_range_negative(self):
        """Test formatting of negative dollar values."""
        test_cases = [
            (-1.00, "-$1.00"),
            (-1.23, "-$1.23"),
            (-100.00, "-$100.00"),
            (-999.99, "-$999.99"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_thousands_range(self):
        """Test formatting of thousand values ($1,000 - $999,999) with K suffix."""
        test_cases = [
            (1000.00, "$1.00k"),
            (1500.50, "$1.50k"),
            (1523.45, "$1.52k"),
            (10000.00, "$10.00k"),
            (250000.00, "$250.00k"),
            (999999.99, "$1000.00k"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_thousands_range_negative(self):
        """Test formatting of negative thousand values."""
        test_cases = [
            (-1000.00, "-$1.00k"),
            (-1500.50, "-$1.50k"),
            (-250000.00, "-$250.00k"),
            (-999999.99, "-$1000.00k"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_millions_range(self):
        """Test formatting of million values ($1M - $999M) with M suffix."""
        test_cases = [
            (1000000.00, "$1.0M"),
            (2500000.50, "$2.5M"),
            (10000000.00, "$10.0M"),
            (123456789.12, "$123.5M"),
            (999999999.99, "$1000.0M"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_millions_range_negative(self):
        """Test formatting of negative million values."""
        test_cases = [
            (-1000000.00, "-$1.0M"),
            (-2500000.50, "-$2.5M"),
            (-100000000.00, "-$100.0M"),
            (-999999999.99, "-$1000.0M"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_billions_range(self):
        """Test formatting of billion values ($1B+) with B suffix."""
        test_cases = [
            (1000000000.00, "$1.0B"),
            (2500000000.50, "$2.5B"),
            (10000000000.00, "$10.0B"),
            (123456789012.34, "$123.5B"),
            (999999999999.99, "$1000.0B"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_billions_range_negative(self):
        """Test formatting of negative billion values."""
        test_cases = [
            (-1000000000.00, "-$1.0B"),
            (-2500000000.50, "-$2.5B"),
            (-999999999999.99, "-$1000.0B"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_trillions_range(self):
        """Test formatting of trillion values ($1T+) with T suffix."""
        test_cases = [
            (1000000000000.00, "$1.0T"),
            (2500000000000.50, "$2.5T"),
            (10000000000000.00, "$10.0T"),
            (123456789012345.67, "$123.5T"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_trillions_range_negative(self):
        """Test formatting of negative trillion values."""
        test_cases = [
            (-1000000000000.00, "-$1.0T"),
            (-2500000000000.50, "-$2.5T"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_zero_value(self):
        """Test formatting of zero value."""
        result = format_currency_market_display_float(0.0)
        self.assertEqual(result, "$0.00")

    def test_custom_currency_symbol(self):
        """Test formatting with custom currency symbols."""
        test_cases = [
            (1000.00, "€", "", "€1.00k"),
            (1000000.00, "£", "", "£1.0M"),
            (100.00, "¥", "", "¥100.00"),
            (0.50, "BTC", "", "BTC0.50"),
        ]

        for value, symbol, suffix, expected in test_cases:
            with self.subTest(value=value, symbol=symbol):
                result = format_currency_market_display_float(value, symbol, suffix)
                self.assertEqual(result, expected)

    def test_custom_suffix(self):
        """Test formatting with custom suffixes."""
        test_cases = [
            (1000.00, "$", " USD", "$1.00k USD"),
            (1000000.00, "$", " (est)", "$1.0M (est)"),
            (100.00, "€", " EUR", "€100.00 EUR"),
        ]

        for value, symbol, suffix, expected in test_cases:
            with self.subTest(value=value, suffix=suffix):
                result = format_currency_market_display_float(value, symbol, suffix)
                self.assertEqual(result, expected)

    def test_boundary_values(self):
        """Test formatting at range boundaries."""
        test_cases = [
            # Just below micro threshold
            (0.000000999, "<$0.000001"),
            # Just above micro threshold
            (0.000001001, "$0.000001"),
            # Just below cents threshold
            (0.00999, "$0.00999"),
            # Just above cents threshold
            (1.00999, "$1.01"),
            # Just below thousands threshold
            (999.99999, "$1000.00"),
            # Just above thousands threshold
            (1000.00001, "$1.00k"),
            # Just below millions threshold
            (999999.99999, "$1000.00k"),
            # Just above millions threshold
            (1000000.00001, "$1.0M"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value, expected=expected):
                result = format_currency_market_display_float(value)
                self.assertEqual(result, expected)

    def test_precision_edge_cases(self):
        """Test precision handling in edge cases."""
        # Test very small values that might cause precision issues
        result = format_currency_market_display_float(0.0000010000001)
        self.assertEqual(result, "$0.000001")

        # Test values that might round unexpectedly
        result = format_currency_market_display_float(1.23456789)
        self.assertEqual(result, "$1.23")

        # Test large values with many decimal places
        result = format_currency_market_display_float(1234567.890123)
        self.assertEqual(result, "$1.2M")


if __name__ == "__main__":
    unittest.main()
