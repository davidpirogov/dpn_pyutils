import unittest

from src.dpn_pyutils.common import PyUtilsLogger, get_logger, initialize_logging


class TestCommon(unittest.TestCase):
    log: PyUtilsLogger

    def setUp(self) -> None:
        super().setUp()

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

        self.assertIn(
            "TRACE:dpn_pyutils.test_common:This is a trace message", cm.output
        )

    def test_debug(self):
        with self.assertLogs("dpn_pyutils.test_common", level="DEBUG") as cm:
            self.log.debug("This is a debug message")

        self.assertIn(
            "DEBUG:dpn_pyutils.test_common:This is a debug message", cm.output
        )

    def test_info(self):
        with self.assertLogs(self.log, level="INFO") as cm:
            self.log.info("This is an info message")

        self.assertIn("INFO:dpn_pyutils.test_common:This is an info message", cm.output)

    def test_warning(self):
        with self.assertLogs(self.log, level="WARNING") as cm:
            self.log.warning("This is a warning message")

        self.assertIn(
            "WARNING:dpn_pyutils.test_common:This is a warning message", cm.output
        )

    def test_error(self):
        with self.assertLogs(self.log, level="ERROR") as cm:
            self.log.error("This is an error message")

        self.assertIn(
            "ERROR:dpn_pyutils.test_common:This is an error message", cm.output
        )

    def test_critical(self):
        with self.assertLogs(self.log, level="CRITICAL") as cm:
            self.log.critical("This is a critical message")

        self.assertIn(
            "CRITICAL:dpn_pyutils.test_common:This is a critical message", cm.output
        )

    def test_fatal(self):
        with self.assertLogs(self.log, level="FATAL") as cm:
            self.log.fatal("This is a fatal message")

        self.assertIn(
            # Fatal is a synonym for critical
            "CRITICAL:dpn_pyutils.test_common:This is a fatal message",
            cm.output,
        )


if __name__ == "__main__":
    unittest.main()
