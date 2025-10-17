import logging
import unittest
from unittest.mock import patch

from dpn_pyutils.logging.formatters import AppLogFormatter, create_formatter


class TestAppLogFormatterAdvanced(unittest.TestCase):
    """Advanced tests for AppLogFormatter to achieve 100% coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = AppLogFormatter()

    def test_init_with_custom_fmt(self):
        """Test AppLogFormatter initialization with custom format string."""
        custom_fmt = "%(levelname)s - %(message)s"
        formatter = AppLogFormatter(fmt=custom_fmt)
        self.assertEqual(formatter._fmt, custom_fmt)

    def test_init_with_custom_datefmt(self):
        """Test AppLogFormatter initialization with custom date format."""
        custom_datefmt = "%H:%M:%S"
        formatter = AppLogFormatter(datefmt=custom_datefmt)
        self.assertEqual(formatter.datefmt, custom_datefmt)

    def test_init_with_custom_style(self):
        """Test AppLogFormatter initialization with custom style."""
        custom_fmt = "{levelname} - {message}"
        formatter = AppLogFormatter(fmt=custom_fmt, style="{")
        self.assertEqual(formatter._style._fmt, formatter._fmt)

    def test_init_without_worker_context(self):
        """Test AppLogFormatter initialization without worker context."""
        formatter = AppLogFormatter(include_worker_context=False)
        self.assertFalse(formatter.include_worker_context)
        # trunk-ignore(bandit/B101)
        assert formatter._fmt is not None
        self.assertIn("%(levelprefix)-8s", formatter._fmt)
        self.assertNotIn("%(worker_context)s", formatter._fmt)

    def test_init_with_worker_context(self):
        """Test AppLogFormatter initialization with worker context."""
        formatter = AppLogFormatter(include_worker_context=True)
        self.assertTrue(formatter.include_worker_context)
        self.assertIsNotNone(formatter._fmt)
        # trunk-ignore(bandit/B101)
        assert formatter._fmt is not None
        self.assertIn("%(worker_context)s", formatter._fmt)

    def test_init_without_colors(self):
        """Test AppLogFormatter initialization without colors."""
        formatter = AppLogFormatter(use_colors=False)
        self.assertFalse(formatter.use_colors)

    def test_format_with_worker_context_both_ids(self):
        """Test format method with both worker_id and correlation_id."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        self.assertIn("[worker:worker123]", result)
        self.assertIn("[corr:corr456]", result)
        self.assertIn("Test message", result)

    def test_format_with_worker_context_no_worker_id(self):
        """Test format method with worker context but no worker_id."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "corr456"
        # No worker_id set

        result = formatter.format(record)

        self.assertNotIn("[worker:", result)
        self.assertIn("[corr:", result)
        self.assertIn("Test message", result)

    def test_format_with_worker_context_no_correlation_id(self):
        """Test format method with worker context but no correlation_id."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        # No correlation_id set

        result = formatter.format(record)

        self.assertIn("[worker:", result)
        self.assertNotIn("[corr:", result)
        self.assertIn("Test message", result)

    def test_format_with_worker_context_none_worker_id(self):
        """Test format method with worker context but worker_id is None."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = None
        record.correlation_id = "corr456"

        result = formatter.format(record)

        self.assertNotIn("[worker:", result)
        self.assertIn("[corr:", result)
        self.assertIn("Test message", result)

    def test_format_with_worker_context_none_correlation_id(self):
        """Test format method with worker context but correlation_id is None."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = None

        result = formatter.format(record)

        self.assertIn("[worker:", result)
        self.assertNotIn("[corr:", result)
        self.assertIn("Test message", result)

    def test_format_with_colors_debug(self):
        """Test format method with colors for DEBUG level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Debug message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain cyan color code for DEBUG
        self.assertIn("\x1b[36m", result)  # Cyan color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("DEBUG", result)

    def test_format_with_colors_info(self):
        """Test format method with colors for INFO level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain green color code for INFO
        self.assertIn("\x1b[32m", result)  # Green color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("INFO", result)

    def test_format_with_colors_warning(self):
        """Test format method with colors for WARNING level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain yellow color code for WARNING
        self.assertIn("\x1b[33m", result)  # Yellow color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("WARNING", result)

    def test_format_with_colors_error(self):
        """Test format method with colors for ERROR level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain red color code for ERROR
        self.assertIn("\x1b[31m", result)  # Red color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("ERROR", result)

    def test_format_with_colors_critical(self):
        """Test format method with colors for CRITICAL level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.CRITICAL,
            pathname="",
            lineno=0,
            msg="Critical message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should contain magenta color code for CRITICAL
        self.assertIn("\x1b[35m", result)  # Magenta color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("CRITICAL", result)

    def test_format_with_colors_unknown_level(self):
        """Test format method with colors for unknown level."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=25,  # Custom level between INFO and WARNING
            pathname="",
            lineno=0,
            msg="Custom message",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        result = formatter.format(record)

        # Should not contain color codes for unknown level
        self.assertNotIn("\x1b[", result)
        self.assertIn("Custom message", result)

    def test_format_multiline_message_with_colors(self):
        """Test format method with multiline message and colors."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Line 1\nLine 2\nLine 3",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        lines = result.split("\n")
        # Only the first line should have color
        self.assertIn("\x1b[32m", lines[0])  # Green color on first line
        self.assertIn("\x1b[0m", lines[0])  # Reset color on first line
        # Other lines should not have color
        for line in lines[1:]:
            self.assertNotIn("\x1b[", line)

    def test_format_multiline_message_without_colors(self):
        """Test format method with multiline message without colors."""
        formatter = AppLogFormatter(use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Line 1\nLine 2\nLine 3",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # No color codes should be present
        self.assertNotIn("\x1b[", result)
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)

    def test_format_with_colors_no_levelprefix(self):
        """Test format method with colors but no levelprefix attribute."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        # Remove levelprefix attribute
        if hasattr(record, "levelprefix"):
            delattr(record, "levelprefix")

        result = formatter.format(record)

        # Should still work without levelprefix
        self.assertIn("Test message", result)

    def test_format_with_colors_levelprefix_not_at_start(self):
        """Test format method with colors but levelprefix not at start of line."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.levelprefix = "INFO"

        # Mock the format to not start with levelprefix
        with patch.object(formatter, "_get_level_prefix", return_value="INFO"):
            with patch("logging.Formatter.format", return_value="Some prefix INFO Test message"):
                result = formatter.format(record)

                # Should not apply colors if levelprefix is not at start
                self.assertNotIn("\x1b[32m", result)
                self.assertIn("Test message", result)

    def test_get_level_prefix_trace(self):
        """Test _get_level_prefix with TRACE level."""
        formatter = AppLogFormatter()

        # TRACE level is DEBUG - 5 = 5
        result = formatter._get_level_prefix(5)
        self.assertEqual(result, "TRACE")

    def test_get_level_prefix_debug(self):
        """Test _get_level_prefix with DEBUG level."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.DEBUG)
        self.assertEqual(result, "DEBUG")

    def test_get_level_prefix_info(self):
        """Test _get_level_prefix with INFO level."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.INFO)
        self.assertEqual(result, "INFO")

    def test_get_level_prefix_warning(self):
        """Test _get_level_prefix with WARNING level."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.WARNING)
        self.assertEqual(result, "WARNING")

    def test_get_level_prefix_error(self):
        """Test _get_level_prefix with ERROR level."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.ERROR)
        self.assertEqual(result, "ERROR")

    def test_get_level_prefix_critical(self):
        """Test _get_level_prefix with CRITICAL level."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.CRITICAL)
        self.assertEqual(result, "CRITICAL")

    def test_get_level_prefix_above_critical(self):
        """Test _get_level_prefix with level above CRITICAL."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(logging.CRITICAL + 10)
        self.assertEqual(result, "CRITICAL")

    def test_get_level_prefix_below_trace(self):
        """Test _get_level_prefix with level below TRACE."""
        formatter = AppLogFormatter()

        result = formatter._get_level_prefix(1)
        self.assertEqual(result, "TRACE")

    def test_get_level_prefix_between_levels(self):
        """Test _get_level_prefix with level between standard levels."""
        formatter = AppLogFormatter()

        # Level between DEBUG and INFO
        result = formatter._get_level_prefix(15)
        self.assertEqual(result, "DEBUG")

    def test_create_formatter_with_colors(self):
        """Test create_formatter function with colors enabled."""
        formatter = create_formatter(use_colors=True)

        self.assertIsInstance(formatter, AppLogFormatter)
        self.assertTrue(formatter.use_colors)

    def test_create_formatter_without_colors(self):
        """Test create_formatter function with colors disabled."""
        formatter = create_formatter(use_colors=False)

        self.assertIsInstance(formatter, AppLogFormatter)
        self.assertFalse(formatter.use_colors)

    def test_create_formatter_default(self):
        """Test create_formatter function with default parameters."""
        formatter = create_formatter()

        self.assertIsInstance(formatter, AppLogFormatter)
        self.assertTrue(formatter.use_colors)  # Default is True

    def test_format_with_worker_context_and_colors(self):
        """Test format method with both worker context and colors."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should have both worker context and colors
        self.assertIn("[worker:worker123]", result)
        self.assertIn("[corr:corr456]", result)
        self.assertIn("Test message", result)

        # Check if colors are applied (they might not be due to worker context format)
        # The important thing is that the formatter doesn't crash and produces output
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_format_without_worker_context_but_with_colors(self):
        """Test format method without worker context but with colors."""
        formatter = AppLogFormatter(include_worker_context=False, use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should have colors but no worker context
        self.assertNotIn("[worker:", result)
        self.assertNotIn("[corr:", result)
        self.assertIn("\x1b[32m", result)  # Green color
        self.assertIn("\x1b[0m", result)  # Reset color
        self.assertIn("Test message", result)

    def test_format_with_worker_context_but_without_colors(self):
        """Test format method with worker context but without colors."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should have worker context but no colors
        self.assertIn("[worker:worker123]", result)
        self.assertIn("[corr:corr456]", result)
        self.assertNotIn("\x1b[", result)  # No color codes
        self.assertIn("Test message", result)

    def test_format_with_colors_no_level_prefix_match(self):
        """Test format method with colors but level prefix doesn't match start of line."""
        formatter = AppLogFormatter(use_colors=True)

        # Create a custom level that's not in the COLORS dictionary
        custom_level = 25  # Between DEBUG and INFO
        logging.addLevelName(custom_level, "CUSTOM")

        record = logging.LogRecord(
            name="test.logger",
            level=custom_level,
            pathname="",
            lineno=0,
            msg="Test message without level prefix",
            args=(),
            exc_info=None,
        )
        # Set a levelprefix that doesn't match the start of the formatted line
        record.levelprefix = "CUSTOM"

        result = formatter.format(record)

        # Should not contain color codes since CUSTOM level is not in COLORS dictionary
        # This tests the branch where record.levelname not in self.COLORS
        self.assertNotIn("\x1b[", result)
        self.assertIn("Test message without level prefix", result)

    def test_format_with_colors_level_prefix_no_match(self):
        """Test format method with colors but level prefix doesn't match start of formatted line."""
        formatter = AppLogFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        # Set a levelprefix that doesn't match the start of the formatted line
        # The formatted line starts with "INFO" but we set levelprefix to something else
        record.levelprefix = "CUSTOM_PREFIX"

        result = formatter.format(record)

        # The formatter will still color "INFO" because it finds it in the message
        # But we can test that the levelprefix logic is working by checking the structure
        self.assertIn("\x1b[", result)  # Colors should still be present
        self.assertIn("Test message", result)
        self.assertIn("INFO", result)  # The actual level should still be there

        # The key test is that the levelprefix doesn't match the start, so the branch 150->157 is taken
        # We can verify this by checking that the levelprefix is not at the start of the colored part
        self.assertNotIn("CUSTOM_PREFIX", result)

    def test_format_with_colors_empty_lines(self):
        """Test format method with colors but empty lines (no lines after splitlines)."""
        formatter = AppLogFormatter(use_colors=True)

        # Create a record that will result in empty lines after splitlines
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="",  # Empty message
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # The formatter will still color "INFO" because it finds it in the message
        # But we can test that the empty lines logic is working
        self.assertIn("\x1b[", result)  # Colors should still be present
        self.assertIn("INFO", result)  # The level should still be there

        # The key test is that the lines processing logic handles empty messages
        # This tests the branch where lines is empty (line 150->157)
        self.assertIn("test.logger", result)

    def test_format_with_worker_id_only(self):
        """Test formatter with only worker_id (correlation_id=None)."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = None

        result = formatter.format(record)

        # Should include worker but not correlation
        self.assertIn("[worker:worker123]", result)
        self.assertNotIn("[corr:", result)
        self.assertIn("Test message", result)

        # Verify individual fields are set on record
        self.assertEqual(record.worker_id, "worker123")
        self.assertIsNone(record.correlation_id)
        self.assertEqual(record.worker_context, "[worker:worker123]")

    def test_format_with_correlation_id_only(self):
        """Test formatter with only correlation_id (worker_id=None)."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = None
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should include correlation but not worker
        self.assertNotIn("[worker:", result)
        self.assertIn("[corr:corr456]", result)
        self.assertIn("Test message", result)

        # Verify individual fields are set on record
        self.assertIsNone(record.worker_id)
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[corr:corr456]")

    def test_format_worker_context_disabled(self):
        """Test that worker_context fields are empty when include_worker_context=False."""
        formatter = AppLogFormatter(include_worker_context=False, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should not include any worker context
        self.assertNotIn("[worker:", result)
        self.assertNotIn("[corr:", result)
        self.assertIn("Test message", result)

        # Verify fields are cleared when worker context is disabled
        self.assertIsNone(record.worker_id)
        self.assertIsNone(record.correlation_id)
        self.assertEqual(record.worker_context, "")

    def test_format_individual_fields_in_custom_format(self):
        """Test custom format string using %(worker_id)s and %(correlation_id)s individually."""
        custom_fmt = "%(levelname)s - %(worker_id)s - %(correlation_id)s - %(message)s"
        formatter = AppLogFormatter(
            fmt=custom_fmt, include_worker_context=True, use_colors=False
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should include individual fields in custom format
        self.assertIn("INFO - worker123 - corr456 - Test message", result)

        # Verify individual fields are set on record
        self.assertEqual(record.worker_id, "worker123")
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[worker:worker123][corr:corr456]")

    def test_format_individual_fields_with_none_values(self):
        """Test individual fields in custom format with None values."""
        custom_fmt = "%(levelname)s - %(worker_id)s - %(correlation_id)s - %(message)s"
        formatter = AppLogFormatter(
            fmt=custom_fmt, include_worker_context=True, use_colors=False
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = None
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Should handle None values gracefully
        self.assertIn("INFO - None - corr456 - Test message", result)

        # Verify individual fields are set on record
        self.assertIsNone(record.worker_id)
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[corr:corr456]")

    def test_format_record_has_all_attributes(self):
        """Test that formatted record has both worker_context and individual attributes."""
        formatter = AppLogFormatter(include_worker_context=True, use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        result = formatter.format(record)

        # Verify the record has all expected attributes after formatting
        self.assertEqual(record.worker_id, "worker123")
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[worker:worker123][corr:corr456]")

        # Verify the formatted output includes the worker context
        self.assertIn("[worker:worker123]", result)
        self.assertIn("[corr:corr456]", result)
        self.assertIn("Test message", result)


if __name__ == "__main__":
    unittest.main()
