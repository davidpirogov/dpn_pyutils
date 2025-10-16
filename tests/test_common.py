import unittest
import warnings

import dpn_pyutils  # noqa
from dpn_pyutils.logging.init import PyUtilsLogger
from dpn_pyutils.logging.logger import get_logger_fqn, get_logger
from dpn_pyutils.logging.init import initialize_logging


class TestCommonModule(unittest.TestCase):
    """
    Tests for the deprecated common module.

    This module is deprecated and will be removed in future releases.
    These tests ensure the deprecation warning is properly issued and
    that all imports remain functional during the deprecation period.
    """

    def test_deprecation_warning_issued(self):
        """Test that importing dpn_pyutils.common issues a DeprecationWarning."""
        # Clear any existing warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Import the common module to trigger the warning
            # We need to reload it since it might already be imported
            import sys
            if "dpn_pyutils.common" in sys.modules:
                del sys.modules["dpn_pyutils.common"]

            import dpn_pyutils.common  # noqa

            # Verify that a warning was issued
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("dpn_pyutils.common module is deprecated", str(w[0].message))
            self.assertIn("will be removed in future releases", str(w[0].message))

    def test_logging_imports_available(self):
        """Test that all logging-related imports are accessible from common module."""
        import dpn_pyutils.common  # noqa

        # Test that logging classes and functions are accessible
        self.assertTrue(callable(PyUtilsLogger))
        self.assertTrue(callable(get_logger_fqn))
        self.assertTrue(callable(get_logger))
        self.assertTrue(callable(initialize_logging))

    def test_common_module_functionality(self):
        """Test that common module functionality works during deprecation period."""
        # Import with warning suppression to avoid test failure
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            import dpn_pyutils.common  # noqa

        # Test that we can still access logging functionality
        logger = get_logger("test.module")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test.module")

        # Test that we can get a fully qualified logger name
        fqn_logger = get_logger_fqn("test.module")
        self.assertIsNotNone(fqn_logger)
        self.assertEqual(fqn_logger.name, "test.module")


if __name__ == "__main__":
    unittest.main()
