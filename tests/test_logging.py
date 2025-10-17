import io
import logging
import unittest
import uuid

from dpn_pyutils.logging import (
    ContextualLoggerAdapter,
    PyUtilsLogger,
    get_contextual_logger,
    get_logger,
    get_worker_logger,
    initialize_logging,
    initialize_logging_safe,
    reset_state,
    set_logging_context,
    clear_logging_context,
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

    def test_worker_logger_with_none_worker_id(self):
        """Test worker logger with None worker_id but valid correlation_id."""
        worker_id = None
        correlation_id = str(uuid.uuid4())

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        worker_log.info("Task with no worker ID")
        output = self.captured_output.getvalue()

        # Should not include worker context but should include correlation
        self.assertNotIn("[worker:", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Task with no worker ID", output)

    def test_worker_logger_with_none_correlation_id(self):
        """Test worker logger with valid worker_id but None correlation_id."""
        worker_id = 42
        correlation_id = None

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        worker_log.info("Task with no correlation ID")
        output = self.captured_output.getvalue()

        # Should include worker context but not correlation
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertNotIn("[corr:", output)
        self.assertIn("Task with no correlation ID", output)

    def test_worker_logger_record_attributes(self):
        """Test that worker logger sets both worker_context and individual fields on log records."""
        worker_id = 99
        correlation_id = str(uuid.uuid4())

        worker_log = get_worker_logger("test_worker", worker_id, correlation_id)

        # Create a custom handler to capture the log record
        class RecordCaptureHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.record = None

            def emit(self, record):
                self.record = record

        handler = RecordCaptureHandler()
        handler.setFormatter(AppLogFormatter(include_worker_context=True, use_colors=False))
        worker_log.logger.addHandler(handler)

        worker_log.debug("Test message")

        # Verify the record has all the expected attributes
        self.assertIsNotNone(handler.record)
        self.assertEqual(handler.record.worker_id, worker_id)
        self.assertEqual(handler.record.correlation_id, correlation_id)
        self.assertIn(f"[worker:{worker_id}]", handler.record.worker_context)
        self.assertIn(f"[corr:{correlation_id}]", handler.record.worker_context)


class TestContextualLogger(unittest.TestCase):
    """Test contextual logger functionality using contextvars."""

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
        self.test_logger = logging.getLogger("dpn_pyutils.test_contextual")
        self.test_logger.addHandler(self.test_handler)

    def tearDown(self) -> None:
        super().tearDown()
        clear_logging_context()

    def test_contextual_logger_with_context(self):
        """Test that get_contextual_logger returns ContextualLoggerAdapter and includes context when set."""
        worker_id = "Worker-1"
        correlation_id = str(uuid.uuid4())

        # Get contextual logger first (before context is set)
        contextual_log = get_contextual_logger("test_contextual")

        # Should always be a ContextualLoggerAdapter
        self.assertIsInstance(contextual_log, ContextualLoggerAdapter)

        # Set context
        set_logging_context(worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        contextual_log.debug("Processing with context")
        output = self.captured_output.getvalue()

        # Should include worker context
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Processing with context", output)

    def test_contextual_logger_without_context(self):
        """Test that get_contextual_logger returns ContextualLoggerAdapter but no context when not set."""
        # Ensure no context is set
        clear_logging_context()

        # Get contextual logger
        contextual_log = get_contextual_logger("test_contextual")

        # Should always be a ContextualLoggerAdapter
        self.assertIsInstance(contextual_log, ContextualLoggerAdapter)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        contextual_log.debug("Processing without context")
        output = self.captured_output.getvalue()

        # Should not include worker context
        self.assertNotIn("[worker:", output)
        self.assertNotIn("[corr:", output)
        self.assertIn("Processing without context", output)

    def test_contextual_logger_with_partial_context_worker_only(self):
        """Test contextual logger with only worker_id set."""
        worker_id = "Worker-2"
        correlation_id = None

        # Set partial context
        set_logging_context(worker_id, correlation_id)

        contextual_log = get_contextual_logger("test_contextual")

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        contextual_log.info("Processing with worker only")
        output = self.captured_output.getvalue()

        # Should include worker but not correlation
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertNotIn("[corr:", output)
        self.assertIn("Processing with worker only", output)

    def test_contextual_logger_with_partial_context_correlation_only(self):
        """Test contextual logger with only correlation_id set."""
        worker_id = None
        correlation_id = str(uuid.uuid4())

        # Set partial context
        set_logging_context(worker_id, correlation_id)

        contextual_log = get_contextual_logger("test_contextual")

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        contextual_log.info("Processing with correlation only")
        output = self.captured_output.getvalue()

        # Should include correlation but not worker
        self.assertNotIn("[worker:", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Processing with correlation only", output)

    def test_context_propagation(self):
        """Test that context propagates through nested function calls."""
        worker_id = "Worker-3"
        correlation_id = str(uuid.uuid4())

        # Set context
        set_logging_context(worker_id, correlation_id)

        def nested_function():
            # Get contextual logger in nested function
            log = get_contextual_logger("test_contextual.nested")
            log.debug("Nested function call")
            return log

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        # Call nested function
        nested_log = nested_function()
        output = self.captured_output.getvalue()

        # Should include context from parent
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Nested function call", output)

        # Should be a ContextualLoggerAdapter
        self.assertIsInstance(nested_log, ContextualLoggerAdapter)

    def test_module_level_logger_instantiation(self):
        """Test that contextual logger can be instantiated at module level and still get context."""
        # Simulate module-level instantiation (before context is set)
        module_log = get_contextual_logger("test_contextual.module")
        self.assertIsInstance(module_log, ContextualLoggerAdapter)

        # Set context after logger instantiation
        worker_id = "Worker-Module"
        correlation_id = str(uuid.uuid4())
        set_logging_context(worker_id, correlation_id)

        # Clear any previous output
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        # Use the module-level logger - should get context
        module_log.info("Module-level logger with context")
        output = self.captured_output.getvalue()

        # Should include context even though logger was created before context was set
        self.assertIn(f"[worker:{worker_id}]", output)
        self.assertIn(f"[corr:{correlation_id}]", output)
        self.assertIn("Module-level logger with context", output)

    def test_custom_format_string_with_individual_fields(self):
        """Test that custom format strings with %(worker_id)s and %(correlation_id)s work."""
        # Create a custom handler with individual field format
        custom_output = io.StringIO()
        custom_handler = logging.StreamHandler(custom_output)
        custom_formatter = logging.Formatter(
            fmt="%(levelname)s - %(worker_id)s - %(correlation_id)s - %(message)s"
        )
        custom_handler.setFormatter(custom_formatter)

        # Get contextual logger and add custom handler
        contextual_log = get_contextual_logger("test_contextual.custom")
        contextual_log.logger.addHandler(custom_handler)

        # Test without context
        custom_output.seek(0)
        custom_output.truncate(0)
        contextual_log.info("Test without context")
        output = custom_output.getvalue()

        # Should show None values
        self.assertIn("INFO - None - None - Test without context", output)

        # Test with context
        worker_id = "CustomWorker"
        correlation_id = "custom-task-123"
        set_logging_context(worker_id, correlation_id)

        custom_output.seek(0)
        custom_output.truncate(0)
        contextual_log.info("Test with context")
        output = custom_output.getvalue()

        # Should show actual values
        self.assertIn(f"INFO - {worker_id} - {correlation_id} - Test with context", output)


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
