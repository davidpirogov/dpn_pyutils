import unittest
from pathlib import Path

from dpn_pyutils.exceptions import FileOperationError, FileSaveError, FileOpenError, FileNotFoundError


class TestFileOperationError(unittest.TestCase):
    """
    Tests for the FileOperationError exception class and its subclasses.

    FileOperationError is the base exception class for file operation errors,
    with specialized subclasses for different types of file errors.
    """

    def test_file_operation_error_initialization(self):
        """Test FileOperationError initialization with file path and message."""
        file_path = Path("/test/path/file.txt")
        message = "Test error message"

        error = FileOperationError(file_path, message)

        # Test that attributes are set correctly
        self.assertEqual(error.file_path, file_path)
        self.assertEqual(str(error), message)
        self.assertEqual(error.args[0], message)

    def test_file_operation_error_with_pathlib_path(self):
        """Test FileOperationError with pathlib.Path objects."""
        file_path = Path.home() / "test.txt"
        message = "Path test message"

        error = FileOperationError(file_path, message)

        self.assertEqual(error.file_path, file_path)
        self.assertIsInstance(error.file_path, Path)

    def test_file_operation_error_with_string_path(self):
        """Test FileOperationError with string path (should still work)."""
        file_path = "/test/path/string.txt"
        message = "String path message"

        error = FileOperationError(file_path, message)  # type: ignore

        self.assertEqual(error.file_path, file_path)
        self.assertIsInstance(error.file_path, str)

    def test_file_operation_error_inheritance(self):
        """Test that FileOperationError properly inherits from Exception."""
        file_path = Path("/test/file.txt")
        message = "Inheritance test"

        error = FileOperationError(file_path, message)

        self.assertIsInstance(error, Exception)
        self.assertTrue(issubclass(FileOperationError, Exception))

    def test_file_save_error_inheritance(self):
        """Test that FileSaveError properly inherits from FileOperationError."""
        file_path = Path("/test/save.txt")
        message = "Save error test"

        error = FileSaveError(file_path, message)

        self.assertIsInstance(error, FileOperationError)
        self.assertIsInstance(error, Exception)
        self.assertTrue(issubclass(FileSaveError, FileOperationError))

    def test_file_open_error_inheritance(self):
        """Test that FileOpenError properly inherits from FileOperationError."""
        file_path = Path("/test/open.txt")
        message = "Open error test"

        error = FileOpenError(file_path, message)

        self.assertIsInstance(error, FileOperationError)
        self.assertIsInstance(error, Exception)
        self.assertTrue(issubclass(FileOpenError, FileOperationError))

    def test_file_not_found_error_inheritance(self):
        """Test that FileNotFoundError properly inherits from FileOperationError."""
        file_path = Path("/test/notfound.txt")
        message = "Not found error test"

        error = FileNotFoundError(file_path, message)

        self.assertIsInstance(error, FileOperationError)
        self.assertIsInstance(error, Exception)
        self.assertTrue(issubclass(FileNotFoundError, FileOperationError))

    def test_exception_hierarchy(self):
        """Test the complete exception hierarchy."""
        file_path = Path("/test/hierarchy.txt")

        # Test that all exception types can be raised and caught properly
        exceptions_to_test = [
            (FileOperationError(file_path, "Base error"), FileOperationError),
            (FileSaveError(file_path, "Save error"), FileSaveError),
            (FileOpenError(file_path, "Open error"), FileOpenError),
            (FileNotFoundError(file_path, "Not found error"), FileNotFoundError),
        ]

        for error, error_type in exceptions_to_test:
            with self.subTest(error_type=error_type):
                # Test that error is instance of its own type
                self.assertIsInstance(error, error_type)

                # Test that error is instance of parent types
                self.assertIsInstance(error, FileOperationError)
                self.assertIsInstance(error, Exception)

                # Test that error has correct file_path
                self.assertEqual(error.file_path, file_path)

    def test_exception_with_empty_message(self):
        """Test exception handling with empty message."""
        file_path = Path("/test/empty.txt")

        error = FileOperationError(file_path, "")

        self.assertEqual(error.file_path, file_path)
        self.assertEqual(str(error), "")

    def test_exception_with_none_path(self):
        """Test exception handling with None path."""
        message = "None path test"

        # This should still work (though not ideal practice)
        error = FileOperationError(None, message)  # type: ignore

        self.assertIsNone(error.file_path)
        self.assertEqual(str(error), message)

    def test_exception_repr(self):
        """Test string representation of exceptions."""
        file_path = Path("/test/repr.txt")
        message = "Repr test message"

        error = FileOperationError(file_path, message)

        # The repr should contain the class name and message
        repr_str = repr(error)
        self.assertIn("FileOperationError", repr_str)
        self.assertIn(message, repr_str)

    def test_multiple_instantiation(self):
        """Test that multiple instances work correctly."""
        file_path1 = Path("/test/file1.txt")
        file_path2 = Path("/test/file2.txt")

        error1 = FileOperationError(file_path1, "Error 1")
        error2 = FileOperationError(file_path2, "Error 2")

        # Each error should maintain its own file_path
        self.assertEqual(error1.file_path, file_path1)
        self.assertEqual(error2.file_path, file_path2)
        self.assertNotEqual(error1.file_path, error2.file_path)


if __name__ == "__main__":
    unittest.main()