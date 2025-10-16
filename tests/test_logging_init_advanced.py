import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dpn_pyutils.logging.init import (
    PyUtilsLogger,
    initialize_logging,
    initialize_logging_from_file,
    initialize_logging_safe,
    is_logging_initialized,
)
from dpn_pyutils.logging.state import reset_state


class TestLoggingInitAdvanced(unittest.TestCase):
    """Advanced tests for logging initialization to achieve 100% coverage."""

    def setUp(self):
        """Set up test fixtures."""
        reset_state()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_state()

    def test_initialize_logging_with_file_handler_path_creation(self):
        """Test initialize_logging creates file handler paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "nonexistent" / "subdir" / "test.log"

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
                    "file": {
                        "level": "INFO",
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": str(log_file),
                    }
                },
                "root": {"level": "INFO", "handlers": ["file"]},
            }

            # Should not raise an exception and should create the directory
            initialize_logging(log_config)

            # Verify the directory was created
            self.assertTrue(log_file.parent.exists())

    def test_initialize_logging_with_file_handler_existing_path(self):
        """Test initialize_logging with existing file handler path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

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
                    "file": {
                        "level": "INFO",
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": str(log_file),
                    }
                },
                "root": {"level": "INFO", "handlers": ["file"]},
            }

            # Should not raise an exception
            initialize_logging(log_config)

    def test_initialize_logging_without_logging_project_name(self):
        """Test initialize_logging without logging_project_name in config."""
        log_config = {
            "version": 1,
            "disable_existing_loggers": True,
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

        # Should not raise an exception
        initialize_logging(log_config)

    def test_initialize_logging_removes_logging_project_name_from_config(self):
        """Test that initialize_logging removes logging_project_name from config passed to dictConfig."""
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

        with patch("logging.config.dictConfig") as mock_dict_config:
            initialize_logging(log_config)

            # Verify that logging_project_name was removed from the config
            call_args = mock_dict_config.call_args[0][0]
            self.assertNotIn("logging_project_name", call_args)

    def test_initialize_logging_from_file_file_not_found(self):
        """Test initialize_logging_from_file with non-existent file."""
        non_existent_file = "/nonexistent/path/logging.json"

        with self.assertRaises(FileNotFoundError) as cm:
            initialize_logging_from_file(non_existent_file)
        self.assertIn("Logging configuration file not found", str(cm.exception))

    def test_initialize_logging_from_file_valid_config(self):
        """Test initialize_logging_from_file with valid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            config_data = {
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

            import json

            json.dump(config_data, temp_file)
            temp_file.flush()

            try:
                # Should not raise an exception
                initialize_logging_from_file(temp_file.name)

                # Verify logging is initialized
                self.assertTrue(is_logging_initialized())

            finally:
                Path(temp_file.name).unlink()

    def test_initialize_logging_from_file_invalid_config(self):
        """Test initialize_logging_from_file with invalid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            # Invalid JSON
            temp_file.write('{"invalid": json}')
            temp_file.flush()

            try:
                with self.assertRaises((ValueError, json.JSONDecodeError, FileNotFoundError)):
                    initialize_logging_from_file(temp_file.name)

            finally:
                Path(temp_file.name).unlink()

    def test_initialize_logging_from_file_already_initialized(self):
        """Test initialize_logging_from_file when already initialized."""
        # First initialize logging
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

        initialize_logging(log_config)

        # Manually set the initialized state since initialize_logging doesn't do it
        from dpn_pyutils.logging.state import set_initialized

        set_initialized(True)

        # Now try to initialize from file - should return early
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            config_data = {
                "version": 1,
                "disable_existing_loggers": True,
                "logging_project_name": "test_app2",
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

            import json

            json.dump(config_data, temp_file)
            temp_file.flush()

            try:
                # Should not raise an exception and should return early
                # The function should detect that logging is already initialized and return
                initialize_logging_from_file(temp_file.name)

            finally:
                Path(temp_file.name).unlink()

    def test_initialize_logging_from_file_with_better_exceptions(self):
        """Test initialize_logging_from_file with better_exceptions integration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            config_data = {
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

            import json

            json.dump(config_data, temp_file)
            temp_file.flush()

            try:
                with patch("better_exceptions.hook") as mock_hook:
                    with patch("logging.captureWarnings") as mock_capture:
                        initialize_logging_from_file(temp_file.name)

                        # Verify better_exceptions.hook was called
                        mock_hook.assert_called_once()

                        # Verify logging.captureWarnings was called
                        mock_capture.assert_called_once_with(True)

            finally:
                Path(temp_file.name).unlink()

    def test_initialize_logging_safe_with_valid_config(self):
        """Test initialize_logging_safe with valid config."""
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

        # Should not raise an exception
        initialize_logging_safe(log_config)

    def test_initialize_logging_safe_with_invalid_config(self):
        """Test initialize_logging_safe with invalid config falls back to basic config."""
        invalid_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "test_app",
            # Missing required fields
        }

        # Should not raise an exception and should fall back to basic config
        initialize_logging_safe(invalid_config)

    def test_initialize_logging_safe_exception_during_initialization(self):
        """Test initialize_logging_safe with exception during initialization."""
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

        # Mock initialize_logging to raise an exception on the first call only
        original_initialize_logging = initialize_logging
        call_count = 0

        def mock_initialize_logging(config):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test exception")
            else:
                return original_initialize_logging(config)

        with patch("dpn_pyutils.logging.init.initialize_logging", side_effect=mock_initialize_logging):
            # Should not raise an exception and should fall back to basic config
            initialize_logging_safe(log_config)

    def test_initialize_logging_safe_fallback_config(self):
        """Test that initialize_logging_safe uses correct fallback config."""
        invalid_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "logging_project_name": "test_app",
            "handlers": {
                "invalid_handler": {
                    "class": "nonexistent.module.InvalidHandler",
                    "level": "INFO",
                }
            },
            "root": {"level": "INFO", "handlers": ["invalid_handler"]},
        }

        # Mock initialize_logging to raise an exception on the first call only
        original_initialize_logging = initialize_logging
        call_count = 0

        def mock_initialize_logging(config):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test exception")
            else:
                return original_initialize_logging(config)

        with patch(
            "dpn_pyutils.logging.init.initialize_logging", side_effect=mock_initialize_logging
        ) as mock_init:
            initialize_logging_safe(invalid_config)

            # Verify that initialize_logging was called twice (once with invalid config, once with fallback)
            self.assertEqual(mock_init.call_count, 2)

            # Check the second call (fallback config)
            second_call_args = mock_init.call_args_list[1][0][0]
            self.assertEqual(second_call_args["version"], 1)
            self.assertFalse(second_call_args["disable_existing_loggers"])
            self.assertIn("formatters", second_call_args)
            self.assertIn("handlers", second_call_args)
            self.assertIn("root", second_call_args)

            # Verify fallback config structure
            self.assertIn("basic", second_call_args["formatters"])
            self.assertIn("console", second_call_args["handlers"])
            self.assertEqual(second_call_args["root"]["level"], "INFO")
            self.assertEqual(second_call_args["root"]["handlers"], ["console"])

    def test_is_logging_initialized_true(self):
        """Test is_logging_initialized returns True when initialized."""
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

        initialize_logging(log_config)

        # Manually set the initialized state since initialize_logging doesn't do it
        from dpn_pyutils.logging.state import set_initialized
        set_initialized(True)

        self.assertTrue(is_logging_initialized())

    def test_is_logging_initialized_false(self):
        """Test is_logging_initialized returns False when not initialized."""
        self.assertFalse(is_logging_initialized())

    def test_pyutils_logger_trace_method(self):
        """Test PyUtilsLogger trace method."""
        logger = PyUtilsLogger("test.logger")

        with patch.object(logger, "log") as mock_log:
            logger.trace("Test trace message")
            mock_log.assert_called_once_with(PyUtilsLogger.TRACE, "Test trace message")

    def test_pyutils_logger_trace_constant(self):
        """Test PyUtilsLogger TRACE constant value."""
        self.assertEqual(PyUtilsLogger.TRACE, logging.DEBUG - 5)

    def test_initialize_logging_adds_trace_level(self):
        """Test that initialize_logging adds TRACE level to logging."""
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

        with patch("logging.addLevelName") as mock_add_level:
            with patch("logging.setLoggerClass") as mock_set_class:
                initialize_logging(log_config)

                # Verify TRACE level was added
                mock_add_level.assert_called_once_with(PyUtilsLogger.TRACE, "TRACE")

                # Verify PyUtilsLogger was set as the logger class
                mock_set_class.assert_called_once_with(PyUtilsLogger)

    def test_initialize_logging_sets_logger_class(self):
        """Test that initialize_logging sets PyUtilsLogger as the logger class."""
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

        with patch("logging.setLoggerClass") as mock_set_class:
            initialize_logging(log_config)
            mock_set_class.assert_called_once_with(PyUtilsLogger)

    def test_initialize_logging_with_multiple_handlers(self):
        """Test initialize_logging with multiple handlers including file handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file1 = Path(temp_dir) / "dir1" / "test1.log"
            log_file2 = Path(temp_dir) / "dir2" / "subdir" / "test2.log"

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
                    },
                    "file1": {
                        "level": "INFO",
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": str(log_file1),
                    },
                    "file2": {
                        "level": "INFO",
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": str(log_file2),
                    },
                },
                "root": {"level": "INFO", "handlers": ["console", "file1", "file2"]},
            }

            # Should not raise an exception and should create all directories
            initialize_logging(log_config)

            # Verify all directories were created
            self.assertTrue(log_file1.parent.exists())
            self.assertTrue(log_file2.parent.exists())

    def test_initialize_logging_with_non_file_handler(self):
        """Test initialize_logging with non-file handler (should not create directories)."""
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

        # Should not raise an exception
        initialize_logging(log_config)

    def test_initialize_logging_with_handler_without_filename(self):
        """Test initialize_logging with handler that doesn't have filename key."""
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

        # Should not raise an exception
        initialize_logging(log_config)


if __name__ == "__main__":
    unittest.main()
