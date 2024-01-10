import tempfile
import unittest
from pathlib import Path

from src.dpn_pyutils.file import (
    read_file_csv,
    read_file_json,
    read_file_text,
    save_file_csv,
    save_file_json,
    save_file_text,
)


class FileModuleTests(unittest.TestCase):
    """
    Tests the file module
    """

    def test_save_and_read_file_json(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            data = {"key": "value"}

            save_file_json(Path(temp_file.name), data, overwrite=True)

            # Verify that the file was saved correctly
            saved_data = read_file_json(Path(temp_file.name))
            self.assertEqual(saved_data, data)

    def test_save_and_read_file_text(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            data = "Hello, World!"

            save_file_text(Path(temp_file.name), data, overwrite=True)

            saved_data = read_file_text(Path(temp_file.name))
            self.assertEqual(saved_data, data)

    def test_save_and_read_file_csv(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            data = [["name", "age"], ["John", "30"], ["Jane", "25"]]

            save_file_csv(Path(temp_file.name), data, overwrite=True)

            saved_data = read_file_csv(Path(temp_file.name))
            self.assertEqual(saved_data, data)


if __name__ == "__main__":
    unittest.main()
