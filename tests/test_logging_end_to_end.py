import io
import logging
import logging.config
import unittest

import pytest

from dpn_pyutils.logging.context import (
    clear_logging_context,
    get_contextual_logger,
    set_logging_context,
)
from dpn_pyutils.logging import reset_state


@pytest.mark.xdist_group(name="serial_group")
class TestContextualLoggerIntegration(unittest.TestCase):
    """Integration tests for ContextualLoggerAdapter that need to run in isolation."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset logging state and clear any existing context
        reset_state()
        clear_logging_context()

    def tearDown(self):
        """Clean up after tests."""
        # Clear context and reset state after each test
        clear_logging_context()
        reset_state()

    def test_contextual_logger_integration_with_formatter(self):
        """Test end-to-end integration with AppLogFormatter."""
        # Use a unique logger name to avoid interference
        unique_logger_name = f"integration_test_{id(self)}"

        # Clear all existing loggers to avoid interference from other tests
        for name in list(logging.Logger.manager.loggerDict.keys()):
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)

        # Set up logging configuration with unique logger name
        config = {
            "version": 1,
            "logging_project_name": "test_app",
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "()": "dpn_pyutils.logging.formatters.AppLogFormatter",
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
            "loggers": {unique_logger_name: {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
        }

        # Capture output
        captured_output = io.StringIO()

        # Configure the handler to use our captured output stream
        config["handlers"]["console"]["stream"] = captured_output

        logging.config.dictConfig(config)

        # After dictConfig, we need to manually set the stream on the handler
        # because dictConfig might not handle StringIO objects properly
        logger = get_contextual_logger(unique_logger_name)

        # Get the underlying logger and set the stream on its handlers
        underlying_logger = logger.logger if hasattr(logger, 'logger') else logger
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.stream = captured_output

        # Set context
        set_logging_context("worker123", "corr456")

        # Log message
        logger.info("Integration test message")

        # Verify output includes context
        output = captured_output.getvalue()
        self.assertIn("worker123", output)
        self.assertIn("corr456", output)
        self.assertIn("Integration test message", output)


if __name__ == "__main__":
    unittest.main()
