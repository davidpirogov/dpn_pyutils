import importlib
import sys
import unittest
from unittest.mock import patch


class TestVersionRequirements(unittest.TestCase):
    """Test Python version requirements across all modules."""

    def test_dpn_pyutils_init_version_requirement(self):
        """Test dpn_pyutils.__init__.py version requirement."""
        with patch("sys.version_info", (3, 11)):
            with self.assertRaises(SystemError) as cm:
                import dpn_pyutils

                importlib.reload(dpn_pyutils)
            self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_dpn_pyutils_init_version_requirement_edge_case(self):
        """Test dpn_pyutils.__init__.py version requirement with 3.12."""
        with patch("sys.version_info", (3, 12)):
            # Should not raise an exception
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_dpn_pyutils_init_version_requirement_newer_version(self):
        """Test dpn_pyutils.__init__.py version requirement with newer version."""
        with patch("sys.version_info", (3, 13)):
            # Should not raise an exception
            try:
                import dpn_pyutils  # noqa
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.13")

    def test_dpn_pyutils_logging_init_version_requirement(self):
        """Test dpn_pyutils.logging.__init__.py version requirement."""
        with patch("sys.version_info", (3, 11)):
            with self.assertRaises(SystemError) as cm:
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
            self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_dpn_pyutils_logging_init_version_requirement_edge_case(self):
        """Test dpn_pyutils.logging.__init__.py version requirement with 3.12."""
        with patch("sys.version_info", (3, 12)):
            # Should not raise an exception
            try:
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_dpn_pyutils_time_init_version_requirement(self):
        """Test dpn_pyutils.time.__init__.py version requirement."""
        with patch("sys.version_info", (3, 11)):
            with self.assertRaises(SystemError) as cm:
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_dpn_pyutils_time_init_version_requirement_edge_case(self):
        """Test dpn_pyutils.time.__init__.py version requirement with 3.12."""
        with patch("sys.version_info", (3, 12)):
            # Should not raise an exception
            try:
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_version_requirement_message_consistency(self):
        """Test that all modules have consistent version requirement messages."""
        with patch("sys.version_info", (3, 11)):
            modules_to_test = [
                "dpn_pyutils",
                "dpn_pyutils.logging",
                "dpn_pyutils.time",
            ]

            for module_name in modules_to_test:
                with self.subTest(module=module_name):
                    with self.assertRaises(SystemError) as cm:
                        module = __import__(module_name)
                        importlib.reload(module)
                    self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_version_requirement_with_patch_cleanup(self):
        """Test that version requirement patches are properly cleaned up."""
        # Test that we can import normally after patching
        with patch("sys.version_info", (3, 13)):
            try:
                import dpn_pyutils  # noqa
                import dpn_pyutils.logging  # noqa
                import dpn_pyutils.time  # noqa
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.13")

        # Test that we can still import normally after the patch is removed
        try:
            import dpn_pyutils  # noqa
            import dpn_pyutils.logging  # noqa
            import dpn_pyutils.time  # noqa
        except SystemError:
            self.fail("SystemError should not be raised for current Python version")

    def test_version_requirement_with_different_patch_scopes(self):
        """Test version requirement with different patch scopes."""
        # Test with patch at module level
        with patch("sys.version_info", (3, 11)):
            with self.assertRaises(SystemError):
                import dpn_pyutils
                importlib.reload(dpn_pyutils)

        # Test with patch at function level
        def test_function():
            with patch("sys.version_info", (3, 11)):
                with self.assertRaises(SystemError):
                    import dpn_pyutils
                    importlib.reload(dpn_pyutils)

        test_function()

    def test_version_requirement_with_context_manager(self):
        """Test version requirement with context manager approach."""
        # Test that the context manager properly restores the original value
        original_version = sys.version_info

        with patch("sys.version_info", (3, 11)):
            self.assertEqual(sys.version_info, (3, 11))
            with self.assertRaises(SystemError):
                import dpn_pyutils
                importlib.reload(dpn_pyutils)

        # Verify original version is restored
        self.assertEqual(sys.version_info, original_version)

    def test_version_requirement_with_multiple_patches(self):
        """Test version requirement with multiple patches in sequence."""
        with patch("sys.version_info", (3, 11)):
            with self.assertRaises(SystemError):
                import dpn_pyutils
                importlib.reload(dpn_pyutils)

        with patch("sys.version_info", (3, 12)):
            try:
                import dpn_pyutils  # noqa
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

        with patch("sys.version_info", (3, 13)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.13")

    def test_version_requirement_with_nested_patches(self):
        """Test version requirement with nested patches."""
        with patch("sys.version_info", (3, 12)):
            with patch("sys.version_info", (3, 11)):
                with self.assertRaises(SystemError):
                    import dpn_pyutils
                    importlib.reload(dpn_pyutils)

            # Should still work with outer patch
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_version_requirement_with_patch_object(self):
        """Test version requirement with patch.object approach."""
        with patch.object(sys, "version_info", (3, 11)):
            with self.assertRaises(SystemError) as cm:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_version_requirement_with_patch_object_edge_case(self):
        """Test version requirement with patch.object and edge case version."""
        with patch.object(sys, "version_info", (3, 12)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_version_requirement_with_patch_object_newer_version(self):
        """Test version requirement with patch.object and newer version."""
        with patch.object(sys, "version_info", (3, 13)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.13")

    def test_version_requirement_with_patch_object_cleanup(self):
        """Test that patch.object properly cleans up."""
        original_version = sys.version_info

        with patch.object(sys, "version_info", (3, 11)):
            self.assertEqual(sys.version_info, (3, 11))
            with self.assertRaises(SystemError):
                import dpn_pyutils
                importlib.reload(dpn_pyutils)

        # Verify original version is restored
        self.assertEqual(sys.version_info, original_version)

    def test_version_requirement_with_patch_object_multiple_modules(self):
        """Test version requirement with patch.object for multiple modules."""
        with patch.object(sys, "version_info", (3, 11)):
            modules_to_test = [
                "dpn_pyutils",
                "dpn_pyutils.logging",
                "dpn_pyutils.time",
            ]

            for module_name in modules_to_test:
                with self.subTest(module=module_name):
                    with self.assertRaises(SystemError) as cm:
                        module = __import__(module_name)
                        importlib.reload(module)
                    self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_version_requirement_with_patch_object_edge_cases(self):
        """Test version requirement with patch.object for edge cases."""
        with patch.object(sys, "version_info", (3, 12)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12")

    def test_version_requirement_with_patch_object_newer_versions(self):
        """Test version requirement with patch.object for newer versions."""
        newer_versions = [(3, 13), (3, 14), (4, 0)]

        for version in newer_versions:
            with self.subTest(version=version):
                with patch.object(sys, "version_info", version):
                    try:
                        import dpn_pyutils  # noqa
                        import dpn_pyutils.logging  # noqa
                        import dpn_pyutils.time  # noqa
                    except SystemError:
                        self.fail(f"SystemError should not be raised for Python {version}")

    def test_version_requirement_with_patch_object_older_versions(self):
        """Test version requirement with patch.object for older versions."""
        older_versions = [(3, 11), (3, 10), (3, 9), (3, 8), (3, 7)]

        for version in older_versions:
            with self.subTest(version=version):
                with patch.object(sys, "version_info", version):
                    with self.assertRaises(SystemError) as cm:
                        import dpn_pyutils
                        importlib.reload(dpn_pyutils)
                    self.assertIn("dpn_pyutils requires Python version >= 3.12", str(cm.exception))

    def test_version_requirement_with_patch_object_exact_version(self):
        """Test version requirement with patch.object for exact version."""
        with patch.object(sys, "version_info", (3, 12, 0)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.0")

    def test_version_requirement_with_patch_object_minor_version(self):
        """Test version requirement with patch.object for minor version."""
        with patch.object(sys, "version_info", (3, 12, 1)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.1")

    def test_version_requirement_with_patch_object_micro_version(self):
        """Test version requirement with patch.object for micro version."""
        with patch.object(sys, "version_info", (3, 12, 0, "final", 0)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.0 final")

    def test_version_requirement_with_patch_object_alpha_version(self):
        """Test version requirement with patch.object for alpha version."""
        with patch.object(sys, "version_info", (3, 12, 0, "alpha", 1)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.0a1")

    def test_version_requirement_with_patch_object_beta_version(self):
        """Test version requirement with patch.object for beta version."""
        with patch.object(sys, "version_info", (3, 12, 0, "beta", 1)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.0b1")

    def test_version_requirement_with_patch_object_rc_version(self):
        """Test version requirement with patch.object for release candidate version."""
        with patch.object(sys, "version_info", (3, 12, 0, "candidate", 1)):
            try:
                import dpn_pyutils
                importlib.reload(dpn_pyutils)
                import dpn_pyutils.logging
                importlib.reload(dpn_pyutils.logging)
                import dpn_pyutils.time
                importlib.reload(dpn_pyutils.time)
            except SystemError:
                self.fail("SystemError should not be raised for Python 3.12.0rc1")


if __name__ == "__main__":
    unittest.main()
