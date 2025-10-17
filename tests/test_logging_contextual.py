import io
import logging
import logging.config
import unittest

from dpn_pyutils.logging.context import (
    ContextualLoggerAdapter,
    clear_logging_context,
    get_contextual_logger,
    get_logging_context,
    has_logging_context,
    set_logging_context,
)
from dpn_pyutils.logging.formatters import AppLogFormatter
from dpn_pyutils.logging.schemas import LogRecord


class TestAppLogFormatterContextual(unittest.TestCase):
    """Tests for AppLogFormatter using dictionary configuration for contextual logging."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "app",
            "formatters": {
                "default": {
                    "()": "dpn_pyutils.logging.formatters.AppLogFormatter",
                    "fmt": "%(levelname)s - %(worker_id)s - %(correlation_id)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "use_colors": True,
                    "include_worker_context": True,
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {"app": {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
            "root": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
        }

    def tearDown(self):
        """Clean up after tests."""
        # Reset logging configuration
        logging.config.dictConfig(self.config)

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

    def test_dict_config_with_both_worker_and_correlation_ids(self):
        """Test dictionary config with both worker_id and correlation_id present."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with worker context
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with both IDs",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of worker context
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Test message with both IDs", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "worker123")
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[worker:worker123][corr:corr456]")

    def test_dict_config_with_worker_id_only(self):
        """Test dictionary config with only worker_id present."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with only worker_id
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with worker ID only",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker789"
        record.correlation_id = None

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of worker_id and absence of correlation_id
        self.assertIn("worker789", output)
        self.assertNotIn("corr", output)
        self.assertIn("Test message with worker ID only", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "worker789")
        self.assertEqual(record.correlation_id, "")
        self.assertEqual(record.worker_context, "[worker:worker789]")

    def test_dict_config_with_correlation_id_only(self):
        """Test dictionary config with only correlation_id present."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with only correlation_id
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with correlation ID only",
            args=(),
            exc_info=None,
        )
        record.worker_id = None
        record.correlation_id = "corr999"

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of correlation_id and absence of worker_id
        self.assertIn("corr999", output)
        self.assertNotIn("worker", output)
        self.assertIn("Test message with correlation ID only", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "")
        self.assertEqual(record.correlation_id, "corr999")
        self.assertEqual(record.worker_context, "[corr:corr999]")

    def test_dict_config_with_no_worker_context(self):
        """Test dictionary config with no worker context values."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with no worker context
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with no context",
            args=(),
            exc_info=None,
        )
        # No worker_id or correlation_id set

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify absence of worker context
        self.assertNotIn("worker", output)
        self.assertNotIn("corr", output)
        self.assertIn("Test message with no context", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "")
        self.assertEqual(record.correlation_id, "")
        self.assertEqual(record.worker_context, "")

    def test_dict_config_with_none_values(self):
        """Test dictionary config with None values for worker context."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with None values
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with None values",
            args=(),
            exc_info=None,
        )
        record.worker_id = None
        record.correlation_id = None

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify absence of worker context
        self.assertNotIn("worker", output)
        self.assertNotIn("corr", output)
        self.assertIn("Test message with None values", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "")
        self.assertEqual(record.correlation_id, "")
        self.assertEqual(record.worker_context, "")

    def test_dict_config_worker_context_disabled(self):
        """Test dictionary config with worker context disabled."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to disable worker context
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output
        config["formatters"]["default"]["include_worker_context"] = False

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with worker context
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with some context disabled",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify absence of context even when values are set
        self.assertNotIn("worker", output)
        self.assertNotIn("corr", output)
        self.assertIn("Test message with some context disabled", output)

        # Verify the record has cleared attributes
        self.assertEqual(record.worker_id, "")
        self.assertEqual(record.correlation_id, "")
        self.assertEqual(record.worker_context, "")

    def test_dict_config_with_colors_and_worker_context(self):
        """Test dictionary config with colors and worker context enabled."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with worker context
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with colors and worker context",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of worker context
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Test message with colors and worker context", output)

        # Colors might be present (depending on formatter implementation)
        # The important thing is that the formatter doesn't crash
        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)

    def test_dict_config_with_different_log_levels(self):
        """Test dictionary config with different log levels and worker context."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Test different log levels
        levels = [
            (logging.DEBUG, "Debug message"),
            (logging.INFO, "Info message"),
            (logging.WARNING, "Warning message"),
            (logging.ERROR, "Error message"),
            (logging.CRITICAL, "Critical message"),
        ]

        for level, message in levels:
            # Create a custom log record with worker context
            record = LogRecord(
                name="app.test",
                level=level,
                pathname="",
                lineno=0,
                msg=message,
                args=(),
                exc_info=None,
            )
            record.worker_id = f"worker_{level}"
            record.correlation_id = f"corr_{level}"

            # Log the message
            logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of worker context for all levels
        for level, message in levels:
            self.assertIn(f"worker_{level}", output)
            self.assertIn(f"corr_{level}", output)
            self.assertIn(message, output)

    def test_dict_config_custom_format_string(self):
        """Test dictionary config with custom format string including individual fields."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config with custom format string
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get logger
        logger = logging.getLogger("app")

        # Create a custom log record with worker context
        record = LogRecord(
            name="app.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message with custom format",
            args=(),
            exc_info=None,
        )
        record.worker_id = "worker123"
        record.correlation_id = "corr456"

        # Log the message
        logger.handle(record)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of individual fields in custom format
        self.assertIn("\x1b[32mINFO\x1b[0m - worker123 - corr456 - Test message with custom format", output)

        # Verify the record has the expected attributes
        self.assertEqual(record.worker_id, "worker123")
        self.assertEqual(record.correlation_id, "corr456")
        self.assertEqual(record.worker_context, "[worker:worker123][corr:corr456]")

    def test_dict_config_multiple_loggers(self):
        """Test dictionary config with multiple loggers and worker context."""
        # Capture stdout
        captured_output = io.StringIO()

        # Update config to use captured output
        config = self.config.copy()
        config["handlers"]["console"]["stream"] = captured_output

        # Apply configuration
        logging.config.dictConfig(config)

        # Get different loggers
        logger1 = logging.getLogger("app.module1")
        logger2 = logging.getLogger("app.module2")

        # Create log records for different loggers
        record1 = LogRecord(
            name="app.module1",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message from module1",
            args=(),
            exc_info=None,
        )
        record1.worker_id = "worker1"
        record1.correlation_id = "corr1"

        record2 = LogRecord(
            name="app.module2",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message from module2",
            args=(),
            exc_info=None,
        )
        record2.worker_id = "worker2"
        record2.correlation_id = "corr2"

        # Log the messages
        logger1.handle(record1)
        logger2.handle(record2)

        # Get the output
        output = captured_output.getvalue()

        # Verify presence of worker context for both loggers
        self.assertIn("worker1", output)
        self.assertIn("corr1", output)
        self.assertIn("Message from module1", output)
        self.assertIn("worker2", output)
        self.assertIn("corr2", output)
        self.assertIn("Message from module2", output)

        # Verify the records have the expected attributes
        self.assertEqual(record1.worker_id, "worker1")
        self.assertEqual(record1.correlation_id, "corr1")
        self.assertEqual(record1.worker_context, "[worker:worker1][corr:corr1]")

        self.assertEqual(record2.worker_id, "worker2")
        self.assertEqual(record2.correlation_id, "corr2")
        self.assertEqual(record2.worker_context, "[worker:worker2][corr:corr2]")


class TestContextualLoggerAdapter(unittest.TestCase):
    """Tests for ContextualLoggerAdapter and context management functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing context
        clear_logging_context()

    def tearDown(self):
        """Clean up after tests."""
        # Clear context after each test
        clear_logging_context()
        # Reset logging configuration
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.WARNING)

    def test_set_and_get_logging_context(self):
        """Test setting and retrieving logging context."""
        # Test initial state (should be None)
        worker_id, correlation_id = get_logging_context()
        self.assertIsNone(worker_id)
        self.assertIsNone(correlation_id)

        # Test setting context
        set_logging_context("worker123", "corr456")
        worker_id, correlation_id = get_logging_context()
        self.assertEqual(worker_id, "worker123")
        self.assertEqual(correlation_id, "corr456")

        # Test updating context
        set_logging_context("worker789", "corr999")
        worker_id, correlation_id = get_logging_context()
        self.assertEqual(worker_id, "worker789")
        self.assertEqual(correlation_id, "corr999")

    def test_clear_logging_context(self):
        """Test clearing logging context."""
        # Set context first
        set_logging_context("worker123", "corr456")
        worker_id, correlation_id = get_logging_context()
        self.assertEqual(worker_id, "worker123")
        self.assertEqual(correlation_id, "corr456")

        # Clear context
        clear_logging_context()
        worker_id, correlation_id = get_logging_context()
        self.assertIsNone(worker_id)
        self.assertIsNone(correlation_id)

    def test_has_logging_context(self):
        """Test has_logging_context function with all branches."""
        # Test with no context
        self.assertFalse(has_logging_context())

        # Test with only worker_id
        set_logging_context("worker123", None)
        self.assertTrue(has_logging_context())

        # Test with only correlation_id
        clear_logging_context()
        set_logging_context(None, "corr456")
        self.assertTrue(has_logging_context())

        # Test with both
        set_logging_context("worker123", "corr456")
        self.assertTrue(has_logging_context())

    def test_has_logging_context_coverage(self):
        """Test has_logging_context function to ensure coverage of lines 168-169."""
        # Clear context first
        clear_logging_context()

        # Test the function directly
        result = has_logging_context()
        self.assertFalse(result)

        # Set context and test again
        set_logging_context("worker123", "corr456")
        result = has_logging_context()
        self.assertTrue(result)

    def test_get_contextual_logger(self):
        """Test creating contextual logger adapter."""
        logger = get_contextual_logger("test.module")

        # Should return a ContextualLoggerAdapter
        self.assertIsInstance(logger, ContextualLoggerAdapter)
        # The logger name might be prefixed depending on configuration
        self.assertTrue(logger.logger.name.endswith("test.module"))

    def test_contextual_logger_with_context_set(self):
        """Test contextual logger with context set."""
        # Set up logging with captured output
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = AppLogFormatter(include_worker_context=True)
        handler.setFormatter(formatter)

        logger = get_contextual_logger("test.module")
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.DEBUG)

        # Set context and log
        set_logging_context("worker123", "corr456")
        logger.info("Test message")

        # Verify context was included
        output = captured_output.getvalue()
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Test message", output)

    def test_contextual_logger_process_method(self):
        """Test process method directly."""
        logger = get_contextual_logger("test.module")

        # Set context
        set_logging_context("worker123", "corr456")

        # Test process method
        msg, kwargs = logger.process("Test message", {})

        # Should return original message and add context to extra
        self.assertEqual(msg, "Test message")
        self.assertIn("extra", kwargs)
        self.assertEqual(kwargs["extra"]["worker_id"], "worker123")
        self.assertEqual(kwargs["extra"]["correlation_id"], "corr456")

    def test_contextual_logger_process_method_with_existing_extra(self):
        """Test process method with existing extra dict."""
        logger = get_contextual_logger("test.module")

        # Set context
        set_logging_context("worker123", "corr456")

        # Test process method with existing extra
        existing_extra = {"existing_key": "existing_value"}
        msg, kwargs = logger.process("Test message", {"extra": existing_extra})

        # Should merge with existing extra
        self.assertEqual(msg, "Test message")
        self.assertIn("extra", kwargs)
        self.assertEqual(kwargs["extra"]["existing_key"], "existing_value")
        self.assertEqual(kwargs["extra"]["worker_id"], "worker123")
        self.assertEqual(kwargs["extra"]["correlation_id"], "corr456")

    def test_contextual_logger_log_method(self):
        """Test _log method with various parameters."""
        # Set up logging with captured output
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = AppLogFormatter(include_worker_context=True)
        handler.setFormatter(formatter)

        logger = get_contextual_logger("test.module")
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.DEBUG)

        # Set context
        set_logging_context("worker123", "corr456")

        # Test _log method with extra=None
        logger._log(logging.INFO, "Test message 1", (), extra=None)

        # Test _log method with existing extra
        existing_extra = {"existing_key": "existing_value"}
        logger._log(logging.INFO, "Test message 2", (), extra=existing_extra)

        # Verify both messages include context
        output = captured_output.getvalue()
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Test message 1", output)
        self.assertIn("Test message 2", output)

    def test_contextual_logger_without_extra_kwargs(self):
        """Test when extra dict doesn't exist in kwargs."""
        logger = get_contextual_logger("test.module")

        # Set context
        set_logging_context("worker123", "corr456")

        # Test process method without extra in kwargs
        msg, kwargs = logger.process("Test message", {})

        # Should create extra dict and add context
        self.assertEqual(msg, "Test message")
        self.assertIn("extra", kwargs)
        self.assertEqual(kwargs["extra"]["worker_id"], "worker123")
        self.assertEqual(kwargs["extra"]["correlation_id"], "corr456")

    def test_comprehensive_coverage(self):
        """Test that covers all functionality in context.py."""
        # Test get_logging_context function
        worker_id, correlation_id = get_logging_context()
        self.assertIsNone(worker_id)
        self.assertIsNone(correlation_id)

        # Test has_logging_context function
        self.assertFalse(has_logging_context())

        # Test process method with context enabled
        logger = get_contextual_logger("test.module")
        set_logging_context("worker123", "corr456")
        msg, kwargs = logger.process("Test message", {})
        self.assertEqual(msg, "Test message")
        self.assertIn("extra", kwargs)
        self.assertEqual(kwargs["extra"]["worker_id"], "worker123")
        self.assertEqual(kwargs["extra"]["correlation_id"], "corr456")

        # Test _log method with extra=None
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = AppLogFormatter(include_worker_context=True)
        handler.setFormatter(formatter)
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.DEBUG)

        logger._log(logging.INFO, "Test _log method", (), extra=None)
        output = captured_output.getvalue()
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Test _log method", output)

    def test_contextual_logger_handles_none_values(self):
        """Test that ContextualLoggerAdapter handles None values correctly."""
        logger = get_contextual_logger("test.module")

        # Test process method with None values
        set_logging_context(None, None)
        msg, kwargs = logger.process("Test message", {})
        self.assertEqual(msg, "Test message")
        self.assertIn("extra", kwargs)
        self.assertIsNone(kwargs["extra"]["worker_id"])
        self.assertIsNone(kwargs["extra"]["correlation_id"])

        # Test _log method with None values (should convert to empty strings)
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = AppLogFormatter(include_worker_context=True)
        handler.setFormatter(formatter)
        logger.logger.addHandler(handler)
        logger.logger.setLevel(logging.DEBUG)

        logger._log(logging.INFO, "Test None values", (), extra=None)
        output = captured_output.getvalue()
        # The formatter should handle None values gracefully
        self.assertIn("Test None values", output)


if __name__ == "__main__":
    unittest.main()
