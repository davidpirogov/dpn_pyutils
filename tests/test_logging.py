import io
import logging
import unittest
import uuid
from dpn_pyutils.logging.formatters import AppLogFormatter

from dpn_pyutils.logging import (
    PyUtilsLogger,
    get_logger,
    get_worker_logger,
    initialize_logging,
    initialize_logging_safe,
    reset_state,
)
from dpn_pyutils.logging.formatters import AppLogFormatter


class TestLogging(unittest.TestCase):
    log: PyUtilsLogger

    def setUp(self) -> None:
        super().setUp()
        # Reset state before each test
        reset_state()

        log_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "dpn_pyutils",
            "formatters": {
                "default": {
                    "()": "logging.Formatter",
                    "fmt": "%(levelname)-8s %(asctime)s.%(msecs)03d [%(threadName)s] %(name)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "level": "TRACE",
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "dpn_pyutils": {
                    "level": "TRACE",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
            "root": {"level": "TRACE", "handlers": ["console"], "propagate": False},
        }

        initialize_logging(log_config)
        self.log = get_logger("test_common")

    def test_trace(self):
        with self.assertLogs("dpn_pyutils.test_common", level="TRACE") as cm:
            self.log.trace("This is a trace message")

        self.assertIn("TRACE:dpn_pyutils.test_common:This is a trace message", cm.output)

    def test_debug(self):
        with self.assertLogs("dpn_pyutils.test_common", level="DEBUG") as cm:
            self.log.debug("This is a debug message")

        self.assertIn("DEBUG:dpn_pyutils.test_common:This is a debug message", cm.output)

    def test_info(self):
        with self.assertLogs(self.log, level="INFO") as cm:
            self.log.info("This is an info message")

        self.assertIn("INFO:dpn_pyutils.test_common:This is an info message", cm.output)

    def test_warning(self):
        with self.assertLogs(self.log, level="WARNING") as cm:
            self.log.warning("This is a warning message")

        self.assertIn("WARNING:dpn_pyutils.test_common:This is a warning message", cm.output)

    def test_error(self):
        with self.assertLogs(self.log, level="ERROR") as cm:
            self.log.error("This is an error message")

        self.assertIn("ERROR:dpn_pyutils.test_common:This is an error message", cm.output)

    def test_critical(self):
        with self.assertLogs(self.log, level="CRITICAL") as cm:
            self.log.critical("This is a critical message")

        self.assertIn("CRITICAL:dpn_pyutils.test_common:This is a critical message", cm.output)

    def test_fatal(self):
        with self.assertLogs(self.log, level="FATAL") as cm:
            self.log.fatal("This is a fatal message")

        self.assertIn(
            # Fatal is a synonym for critical
            "CRITICAL:dpn_pyutils.test_common:This is a fatal message",
            cm.output,
        )


class TestWorkerLogger(unittest.TestCase):
    """Test worker logger functionality."""

    def setUp(self) -> None:
        super().setUp()
        reset_state()

        # Create a custom handler that captures formatted output
        self.captured_output = io.StringIO()

        # Use a formatter that supports worker context
        log_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "dpn_pyutils",
            "formatters": {
                "worker": {
                    "()": "dpn_pyutils.logging.formatters.AppLogFormatter",
                    "include_worker_context": True,
                    "use_colors": False,
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "formatter": "worker",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "dpn_pyutils": {
                    "level": "DEBUG",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
        }

        initialize_logging(log_config)

        # Add our custom handler to capture output

        self.test_handler = logging.StreamHandler(self.captured_output)
        self.test_handler.setFormatter(AppLogFormatter(include_worker_context=True, use_colors=False))

        # Get the logger and add our test handler
        self.test_logger = logging.getLogger("dpn_pyutils.test_worker")
        self.test_logger.addHandler(self.test_handler)

    def test_worker_logger_with_context(self):
        """Test that worker logger includes worker_id and correlation_id in output."""
        worker_id = 42
        correlation_id = str(uuid.uuid4())

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        worker_log.debug("Processing task")
        output = self.captured_output.getvalue()

        # Check that the log message includes worker context
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Processing task", output)

    def test_worker_logger_with_string_worker_id(self):
        """Test worker logger with string worker_id."""
        worker_id = "worker-123"
        correlation_id = str(uuid.uuid4())

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        worker_log.info("Task completed")
        output = self.captured_output.getvalue()

        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertIn(f"[corr:{correlation_id}]", output)

    def test_worker_logger_multiple_messages(self):
        """Test that worker context is consistent across multiple log calls."""
        worker_id = 99
        correlation_id = str(uuid.uuid4())

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        worker_log.debug("Starting task")
        worker_log.info("Task in progress")
        worker_log.warning("Task almost done")
        worker_log.error("Task completed")

        output = self.captured_output.getvalue()

        # All messages should have the same worker context
        lines = output.strip().split("\n")
        for line in lines:
            self.assertIn(f"[worker:{worker_id}]", line)
            self.assertIn(f"[corr:{correlation_id}]", line)


class TestSafeInitialization(unittest.TestCase):
    """Test safe initialization functionality."""

    def setUp(self) -> None:
        super().setUp()
        reset_state()

    def test_safe_initialization_with_valid_config(self):
        """Test that safe initialization works with valid config."""
        log_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "test_app",
            "formatters": {
                "default": {
                    "()": "logging.Formatter",
                    "fmt": "%(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"level": "INFO", "handlers": ["console"]},
        }

        # Should not raise any exceptions
        initialize_logging_safe(log_config)

        # Should be able to get a logger
        log = get_logger("test_module")
        self.assertEqual(log.name, "test_app.test_module")

    def test_safe_initialization_with_invalid_config(self):
        """Test that safe initialization falls back gracefully with invalid config."""
        # Invalid config - missing required fields
        invalid_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "test_app",
            # Missing formatters, handlers, etc.
        }

        # Should not raise any exceptions
        initialize_logging_safe(invalid_config)

        # Should still be able to get a logger (with fallback config)
        log = get_logger("test_module")
        self.assertIsInstance(log, PyUtilsLogger)

    def test_auto_initialization_on_get_logger(self):
        """Test that get_logger_fqn auto-initializes when logging not initialized."""
        reset_state()

        # Should not raise RuntimeError, should auto-initialize
        log = get_logger("test_module")
        self.assertIsInstance(log, PyUtilsLogger)
        self.assertEqual(log.name, "test_module")  # No project name prefix in fallback


if __name__ == "__main__":
    unittest.main()
