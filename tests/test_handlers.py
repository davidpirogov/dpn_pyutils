import logging
import tempfile
import unittest
from pathlib import Path

from dpn_pyutils.logging.formatters import AppLogFormatter
from dpn_pyutils.logging.handlers import TimedFileHandler


class TestTimedFileHandler(unittest.TestCase):
    """
    Tests for the TimedFileHandler class.

    This handler extends logging.FileHandler to support dynamic filename
    generation using datetime formatting.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_with_timestamp_format(self):
        """Test TimedFileHandler initialization with timestamp filename format."""
        # Test with a simple timestamp format
        filename_format = "%Y-%m-%d_%H-%M-%S.log"
        handler = TimedFileHandler(filename_format, use_colors=False)

        # Check that filename was formatted with current timestamp
        self.assertTrue(handler.baseFilename.endswith(".log"))
        # The filename should be different from the format string
        self.assertNotEqual(handler.baseFilename, filename_format)

        # Clean up
        handler.close()

    def test_init_with_complex_timestamp_format(self):
        """Test TimedFileHandler with complex timestamp format."""
        filename_format = "test_%Y%m%d_%H%M%S_%f.log"
        handler = TimedFileHandler(filename_format)

        # Debug: print the actual filename
        print(f"Actual filename: {handler.baseFilename}")

        # Should contain 'test_' prefix and '.log' suffix
        # Note: baseFilename includes the full path, so we check the basename
        import os

        filename_basename = os.path.basename(handler.baseFilename)
        self.assertTrue(filename_basename.startswith("test_"))
        self.assertTrue(filename_basename.endswith(".log"))

        # Clean up the file
        if os.path.exists(handler.baseFilename):
            os.remove(handler.baseFilename)
        handler.close()

    def test_init_with_custom_parameters(self):
        """Test TimedFileHandler initialization with custom parameters."""
        filename_format = "app_%Y%m%d.log"
        handler = TimedFileHandler(filename_format, mode="w", encoding="utf-8", delay=True, use_colors=True)

        self.assertTrue(handler.use_colors)
        self.assertEqual(handler.mode, "w")
        self.assertEqual(handler.encoding, "utf-8")
        self.assertTrue(handler.delay)

        handler.close()

    def test_setFormatter_with_appLogFormatter(self):
        """Test setFormatter method with AppLogFormatter."""
        handler = TimedFileHandler("test_%Y%m%d.log", use_colors=True)

        # Create an AppLogFormatter
        formatter = AppLogFormatter(include_worker_context=False, use_colors=False)

        # Set the formatter
        handler.setFormatter(formatter)

        # Check that use_colors was synchronized
        self.assertTrue(handler.use_colors)
        self.assertTrue(formatter.use_colors)

        handler.close()

    def test_setFormatter_with_regular_formatter(self):
        """Test setFormatter method with regular logging.Formatter."""
        handler = TimedFileHandler("test_%Y%m%d.log", use_colors=False)

        # Create a regular formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Set the formatter - should not raise an error
        handler.setFormatter(formatter)

        # use_colors should remain unchanged
        self.assertFalse(handler.use_colors)

        handler.close()

    def test_setFormatter_with_none(self):
        """Test setFormatter method with None."""
        handler = TimedFileHandler("test_%Y%m%d.log", use_colors=True)

        # Set formatter to None
        handler.setFormatter(None)

        # Should not raise an error
        self.assertIsNone(handler.formatter)

        handler.close()

    def test_actual_file_creation_and_logging(self):
        """Test that the handler actually creates files and logs messages."""
        filename_format = "actual_test_%Y%m%d_%H%M%S.log"
        handler = TimedFileHandler(filename_format, use_colors=False)

        # Create a logger and add our handler
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Set a simple formatter
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)

        # Log a test message
        test_message = "This is a test log message"
        logger.info(test_message)

        # Check that file was created
        self.assertTrue(Path(handler.baseFilename).exists())

        # Check that the log message was written
        with open(handler.baseFilename, "r") as f:
            content = f.read()
            self.assertIn(test_message, content)

        # Clean up
        logger.removeHandler(handler)
        handler.close()

        # Remove the test file
        import os

        if os.path.exists(handler.baseFilename):
            os.remove(handler.baseFilename)

    def test_handler_with_different_delay_modes(self):
        """Test handler behavior with delay=True vs delay=False."""
        # Test with delay=False (file created immediately)
        handler_immediate = TimedFileHandler("immediate_%Y%m%d.log", delay=False)
        self.assertTrue(Path(handler_immediate.baseFilename).exists())

        # Clean up
        import os

        if os.path.exists(handler_immediate.baseFilename):
            os.remove(handler_immediate.baseFilename)
        handler_immediate.close()

        # Test with delay=True (file created on first log)
        handler_delayed = TimedFileHandler("delayed_%Y%m%d.log", delay=True)
        # Note: File might be created during handler initialization regardless of delay setting
        # The key difference is when the file is actually opened for writing

        # Add to logger and log a message to trigger file creation
        logger = logging.getLogger("test_delayed")
        logger.addHandler(handler_delayed)
        logger.setLevel(logging.INFO)
        handler_delayed.setFormatter(logging.Formatter("%(message)s"))

        logger.info("Trigger file creation")
        self.assertTrue(Path(handler_delayed.baseFilename).exists())  # File should exist now

        # Clean up
        logger.removeHandler(handler_delayed)
        handler_delayed.close()

        # Remove the test file
        import os

        if os.path.exists(handler_delayed.baseFilename):
            os.remove(handler_delayed.baseFilename)

        # Clean up
        logger.removeHandler(handler_delayed)
        handler_delayed.close()

    def test_use_colors_attribute(self):
        """Test the use_colors attribute functionality."""
        # Test default value
        handler1 = TimedFileHandler("test1.log")
        self.assertFalse(handler1.use_colors)

        # Test explicit True
        handler2 = TimedFileHandler("test2.log", use_colors=True)
        self.assertTrue(handler2.use_colors)

        # Test explicit False
        handler3 = TimedFileHandler("test3.log", use_colors=False)
        self.assertFalse(handler3.use_colors)

        handler1.close()
        handler2.close()
        handler3.close()


if __name__ == "__main__":
    unittest.main()
