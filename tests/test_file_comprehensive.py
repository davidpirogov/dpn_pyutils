import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

from dpn_pyutils.exceptions import FileOpenError, FileSaveError
from dpn_pyutils.file import (
    append_value_to_filename,
    extract_timestamp_from_snapshot_key,
    get_cachekey,
    get_file_list_from_dir,
    get_timestamp_format_by_ttl_seconds,
    get_timestamp_formatted_file_dir,
    get_valid_file,
    json_serializer,
    prepare_timestamp_datapath,
    read_file_csv,
    read_file_json,
    read_file_text,
    read_file_toml,
    save_file_csv,
    save_file_json,
    save_file_json_opts,
    save_file_text,
)


class TestFileComprehensive(unittest.TestCase):
    """Comprehensive tests for file operations to achieve 100% coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_serializer_datetime(self):
        """Test json_serializer with datetime objects."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = json_serializer(dt)
        self.assertEqual(result, "2023-12-01T12:30:45")

    def test_json_serializer_date(self):
        """Test json_serializer with date objects."""
        from datetime import date

        d = date(2023, 12, 1)
        result = json_serializer(d)
        self.assertEqual(result, "2023-12-01")

    def test_json_serializer_decimal(self):
        """Test json_serializer with decimal objects."""
        import decimal

        dec = decimal.Decimal("123.45")
        result = json_serializer(dec)
        self.assertEqual(result, "123.45")

    def test_json_serializer_unsupported_type(self):
        """Test json_serializer with unsupported type raises TypeError."""
        with self.assertRaises(TypeError) as cm:
            json_serializer({"unsupported": "type"})
        self.assertIn("Type '<class 'dict'>' is not JSON serializable", str(cm.exception))

    def test_read_file_json_file_not_found(self):
        """Test read_file_json with non-existent file."""
        non_existent = self.temp_path / "nonexistent.json"
        with self.assertRaises(FileNotFoundError) as cm:
            read_file_json(non_existent)
        self.assertIn("File with path", str(cm.exception))

    def test_read_file_json_os_error(self):
        """Test read_file_json with OSError during read."""
        test_file = self.temp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        with patch("dpn_pyutils.file.__try_read_file", side_effect=OSError("Read error")):
            with self.assertRaises(FileOpenError) as cm:
                read_file_json(test_file)
            self.assertIn("Error while trying to read file", str(cm.exception))

    def test_read_file_text_file_not_found(self):
        """Test read_file_text with non-existent file."""
        non_existent = self.temp_path / "nonexistent.txt"
        with self.assertRaises(FileNotFoundError) as cm:
            read_file_text(non_existent)
        self.assertIn("File with path", str(cm.exception))

    def test_read_file_text_os_error(self):
        """Test read_file_text with OSError during read."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Hello World")

        with patch("dpn_pyutils.file.__try_read_file", side_effect=OSError("Read error")):
            with self.assertRaises(FileOpenError) as cm:
                read_file_text(test_file)
            self.assertIn("Error while trying to read file", str(cm.exception))

    def test_read_file_toml(self):
        """Test read_file_toml functionality."""
        test_file = self.temp_path / "test.toml"
        test_file.write_text('[section]\nkey = "value"')

        result = read_file_toml(test_file)
        self.assertEqual(result, {"section": {"key": "value"}})

    def test_read_file_csv_custom_delimiter(self):
        """Test read_file_csv with custom delimiter and quote char."""
        test_file = self.temp_path / "test.csv"
        test_file.write_text('name|age\n"John"|30\n"Jane"|25')

        result = read_file_csv(test_file, delimiter="|", quote_char='"')
        expected = [["name", "age"], ["John", "30"], ["Jane", "25"]]
        self.assertEqual(result, expected)

    def test_save_file_text_no_overwrite_existing(self):
        """Test save_file_text without overwrite on existing file."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("existing content")

        with self.assertRaises(FileSaveError) as cm:
            save_file_text(test_file, "new content", overwrite=False)
        self.assertIn(
            "File '{}' exists and the overwrite flag is not set to True!".format(test_file.absolute()),
            str(cm.exception),
        )

    def test_save_file_text_os_error(self):
        """Test save_file_text with OSError during save."""
        test_file = self.temp_path / "test.txt"

        with patch("dpn_pyutils.file.__try_save_file", side_effect=OSError("Write error")):
            with self.assertRaises(FileSaveError) as cm:
                save_file_text(test_file, "content", overwrite=True)
            self.assertIn("Error while trying to save file", str(cm.exception))

    def test_save_file_csv_no_overwrite_existing(self):
        """Test save_file_csv without overwrite on existing file."""
        test_file = self.temp_path / "test.csv"
        test_file.write_text("existing content")

        with self.assertRaises(FileSaveError) as cm:
            save_file_csv(test_file, [["data"]], overwrite=False)
        self.assertIn(
            "File '{}' exists and the overwrite flag is not set to True!".format(test_file.absolute()),
            str(cm.exception),
        )

    def test_save_file_csv_os_error(self):
        """Test save_file_csv with OSError during save."""
        test_file = self.temp_path / "test.csv"

        with patch("dpn_pyutils.file.__try_save_file", side_effect=OSError("Write error")):
            with self.assertRaises(FileSaveError) as cm:
                save_file_csv(test_file, [["data"]], overwrite=True)
            self.assertIn("Error while trying to save file", str(cm.exception))

    def test_save_file_csv_with_escapechar(self):
        """Test save_file_csv with escape character."""
        test_file = self.temp_path / "test.csv"
        data = [["name", "value"], ["test", 'value with "quotes"']]

        save_file_csv(test_file, data, escapechar="\\", overwrite=True)

        result = read_file_csv(test_file)
        self.assertEqual(result, data)

    def test_save_file_json_os_error(self):
        """Test save_file_json with OSError during save."""
        test_file = self.temp_path / "test.json"

        with patch("dpn_pyutils.file.__try_save_file", side_effect=OSError("Write error")):
            with self.assertRaises(FileSaveError) as cm:
                save_file_json(test_file, {"key": "value"}, overwrite=True)
            self.assertIn("Error while trying to save file", str(cm.exception))

    def test_save_file_json_opts_no_overwrite_existing(self):
        """Test save_file_json_opts without overwrite on existing file."""
        test_file = self.temp_path / "test.json"
        test_file.write_text("existing content")

        with self.assertRaises(FileSaveError) as cm:
            save_file_json_opts(test_file, {"key": "value"}, overwrite=False)
        self.assertIn(
            "File '{}' exists and the overwrite flag is not set to True!".format(test_file.absolute()),
            str(cm.exception),
        )

    def test_save_file_json_opts_os_error(self):
        """Test save_file_json_opts with OSError during save."""
        test_file = self.temp_path / "test.json"

        with patch("dpn_pyutils.file.__try_save_file", side_effect=OSError("Write error")):
            with self.assertRaises(FileSaveError) as cm:
                save_file_json_opts(test_file, {"key": "value"}, overwrite=True)
            self.assertIn("Error while trying to save file", str(cm.exception))

    def test_save_file_json_opts_with_custom_options(self):
        """Test save_file_json_opts with custom serializer options."""
        test_file = self.temp_path / "test.json"
        data = {"key": "value"}

        # Test with custom options (using orjson flags)
        save_file_json_opts(test_file, data, overwrite=True, serializer_opts=0)

        result = read_file_json(test_file)
        self.assertEqual(result, data)

    def test_try_save_file_binary_write_with_string_data(self):
        """Test __try_save_file with binary write mode and string data."""
        test_file = self.temp_path / "test.bin"

        # This tests the binary write path with string data conversion
        with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
            with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                with patch("pathlib.Path.replace") as _:
                    # Mock the file write operation
                    with patch("builtins.open", mock_open()) as mock_file:
                        save_file_json(test_file, {"key": "value"}, overwrite=True)
                        mock_file.assert_called()

    def test_try_save_file_exception_cleanup(self):
        """Test __try_save_file exception handling and cleanup."""
        test_file = self.temp_path / "test.json"

        with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
            with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                with patch("builtins.open", side_effect=OSError("Write error")):
                    with patch.object(Path, "exists", return_value=True):
                        with patch.object(Path, "unlink") as mock_unlink:
                            with self.assertRaises(FileSaveError):
                                save_file_json(test_file, {"key": "value"}, overwrite=True)
                            mock_unlink.assert_called_once()

    def test_get_valid_file_with_timestamp(self):
        """Test get_valid_file with timestamp option."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("existing")

        with patch("dpn_pyutils.file.datetime") as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = 1234567890
            result = get_valid_file(self.temp_path, "test.txt", use_timestamp=True)
            self.assertNotEqual(result, test_file)

    def test_get_valid_file_sequential_naming(self):
        """Test get_valid_file with sequential naming."""
        # Create multiple existing files
        for i in range(3):
            (self.temp_path / f"test_{i}.txt").write_text("content")

        result = get_valid_file(self.temp_path, "test_0.txt")
        self.assertFalse(result.exists())

    def test_append_value_to_filename_no_extension(self):
        """Test append_value_to_filename with filename without extension."""
        result = append_value_to_filename("filename", "_suffix")
        self.assertEqual(result, "filename_suffix")

    def test_append_value_to_filename_with_extension(self):
        """Test append_value_to_filename with filename with extension."""
        result = append_value_to_filename("filename.txt", "_suffix")
        self.assertEqual(result, "filename_suffix.txt")

    def test_append_value_to_filename_multiple_extensions(self):
        """Test append_value_to_filename with multiple extensions."""
        result = append_value_to_filename("filename.tar.gz", "_suffix")
        self.assertEqual(result, "filename.tar_suffix.gz")

    def test_get_timestamp_formatted_file_dir_year_resolution(self):
        """Test get_timestamp_formatted_file_dir with YEAR resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "YEAR")
        expected = self.temp_path / "2023"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_month_resolution(self):
        """Test get_timestamp_formatted_file_dir with MONTH resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "MONTH")
        expected = self.temp_path / "2023-12"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_day_resolution(self):
        """Test get_timestamp_formatted_file_dir with DAY resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "DAY")
        expected = self.temp_path / "2023-12-01"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_hour_resolution(self):
        """Test get_timestamp_formatted_file_dir with HOUR resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "HOUR")
        expected = self.temp_path / "2023-12-01/12"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_minute_resolution(self):
        """Test get_timestamp_formatted_file_dir with MINUTE resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "MINUTE")
        expected = self.temp_path / "2023-12-01/12/30"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_second_resolution(self):
        """Test get_timestamp_formatted_file_dir with SECOND resolution."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "SECOND")
        expected = self.temp_path / "2023-12-01/12/30/45"
        self.assertEqual(result, expected)

    def test_get_timestamp_formatted_file_dir_create_dir(self):
        """Test get_timestamp_formatted_file_dir with create_dir=True."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_timestamp_formatted_file_dir(self.temp_path, dt, "HOUR", create_dir=True)
        self.assertTrue(result.exists())

    def test_get_cachekey_with_timestamp(self):
        """Test get_cachekey with provided timestamp."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = get_cachekey(3600, dt)
        self.assertIsInstance(result, str)
        self.assertIn("2023-12-01-12", result)

    def test_get_cachekey_without_timestamp(self):
        """Test get_cachekey without timestamp (uses current time)."""
        result = get_cachekey(3600)
        self.assertIsInstance(result, str)

    def test_get_timestamp_format_by_ttl_seconds_day(self):
        """Test get_timestamp_format_by_ttl_seconds with day TTL."""
        result = get_timestamp_format_by_ttl_seconds(86400)  # 1 day
        self.assertEqual(result, "%Y-%m-%d-000000")

    def test_get_timestamp_format_by_ttl_seconds_hour(self):
        """Test get_timestamp_format_by_ttl_seconds with hour TTL."""
        result = get_timestamp_format_by_ttl_seconds(3600)  # 1 hour
        self.assertEqual(result, "%Y-%m-%d-%H0000")

    def test_get_timestamp_format_by_ttl_seconds_minute(self):
        """Test get_timestamp_format_by_ttl_seconds with minute TTL."""
        result = get_timestamp_format_by_ttl_seconds(60)  # 1 minute
        self.assertEqual(result, "%Y-%m-%d-%H%M00")

    def test_get_timestamp_format_by_ttl_seconds_second(self):
        """Test get_timestamp_format_by_ttl_seconds with second TTL."""
        result = get_timestamp_format_by_ttl_seconds(30)  # 30 seconds
        self.assertEqual(result, "%Y-%m-%d-%H%M%S")

    def test_get_file_list_from_dir(self):
        """Test get_file_list_from_dir functionality."""
        # Create test files
        (self.temp_path / "file1.txt").write_text("content1")
        (self.temp_path / "file2.txt").write_text("content2")
        (self.temp_path / "subdir").mkdir()
        (self.temp_path / "subdir" / "file3.txt").write_text("content3")

        result = get_file_list_from_dir(self.temp_path, "*.txt")
        self.assertEqual(len(result), 3)
        self.assertTrue(all(Path(f).suffix == ".txt" for f in result))

    def test_get_file_list_from_dir_with_mask(self):
        """Test get_file_list_from_dir with specific file mask."""
        # Create test files
        (self.temp_path / "file1.txt").write_text("content1")
        (self.temp_path / "file2.json").write_text("{}")

        result = get_file_list_from_dir(self.temp_path, "*.json")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].endswith("file2.json"))

    def test_extract_timestamp_from_snapshot_key_valid(self):
        """Test extract_timestamp_from_snapshot_key with valid key."""
        key = "trending-snapshot-2021-01-01-143546"
        result = extract_timestamp_from_snapshot_key(key)
        expected = datetime(2021, 1, 1, 14, 35, 46, 0)
        self.assertEqual(result, expected)

    def test_extract_timestamp_from_snapshot_key_invalid(self):
        """Test extract_timestamp_from_snapshot_key with invalid key."""
        key = "invalid-key-format"
        with self.assertRaises(ValueError) as cm:
            extract_timestamp_from_snapshot_key(key)
        self.assertIn("Could not match the snapshot key with a valid regex", str(cm.exception))

    def test_prepare_timestamp_datapath(self):
        """Test prepare_timestamp_datapath functionality."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = prepare_timestamp_datapath(self.temp_path, dt, "DAY", 3600, "prefix_")
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result).endswith(".json"))
        self.assertIn("prefix_", str(result))

    def test_prepare_timestamp_datapath_defaults(self):
        """Test prepare_timestamp_datapath with default parameters."""
        dt = datetime(2023, 12, 1, 12, 30, 45)
        result = prepare_timestamp_datapath(self.temp_path, dt)
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result).endswith(".json"))

    def test_save_file_text_overwrite_false_exception(self):
        """Test save_file_text raises exception when overwrite=False and file exists."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("existing content")

        # This should raise an exception
        with self.assertRaises(FileSaveError) as cm:
            save_file_text(test_file, "new content", overwrite=False)
        self.assertIn("exists and the overwrite flag is not set to True", str(cm.exception))
        self.assertEqual(test_file.read_text(), "existing content")

    def test_save_file_csv_overwrite_false_exception(self):
        """Test save_file_csv raises exception when overwrite=False and file exists."""
        test_file = self.temp_path / "test.csv"
        test_file.write_text("existing,content")

        # This should raise an exception
        with self.assertRaises(FileSaveError) as cm:
            save_file_csv(test_file, [["new", "data"]], overwrite=False)
        self.assertIn("exists and the overwrite flag is not set to True", str(cm.exception))
        self.assertEqual(test_file.read_text(), "existing,content")

    def test_save_file_json_overwrite_false_exception(self):
        """Test save_file_json raises exception when overwrite=False and file exists."""
        test_file = self.temp_path / "test.json"
        test_file.write_text('{"existing": "content"}')

        # This should raise an exception
        with self.assertRaises(FileSaveError) as cm:
            save_file_json(test_file, {"new": "data"}, overwrite=False)
        self.assertIn("exists and the overwrite flag is not set to True", str(cm.exception))
        self.assertEqual(test_file.read_text(), '{"existing": "content"}')

    def test_save_file_json_binary_write_conversion(self):
        """Test save_file_json with binary write mode to trigger conversion path."""
        test_file = self.temp_path / "test.json"

        # Mock the file write to test the binary conversion path
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
                with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                    with patch.object(Path, "exists", return_value=True):
                        with patch.object(Path, "replace") as mock_replace:
                            # This should trigger the binary write conversion path
                            save_file_json(test_file, {"test": "data"}, overwrite=True)
                            mock_file.assert_called()
                            mock_replace.assert_called()

    def test_save_file_json_exception_cleanup_path(self):
        """Test save_file_json exception cleanup when file exists."""
        test_file = self.temp_path / "test.json"

        with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
            with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                with patch("builtins.open", side_effect=OSError("Write error")):
                    with patch.object(Path, "exists", return_value=True):
                        with patch.object(Path, "unlink") as mock_unlink:
                            with self.assertRaises(FileSaveError):
                                save_file_json(test_file, {"test": "data"}, overwrite=True)
                            mock_unlink.assert_called_once()

    def test_save_file_text_binary_write_conversion(self):
        """Test save_file_text with binary write mode to trigger string conversion."""
        test_file = self.temp_path / "test.txt"

        # Mock the file operations to test the binary conversion path
        with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
            with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                with patch("builtins.open", mock_open()) as mock_file:
                    with patch.object(Path, "exists", return_value=True):
                        with patch.object(Path, "replace") as mock_replace:
                            # Test with string data - this should trigger the binary conversion path
                            # when use_binary_write=True and data is not bytes
                            save_file_text(test_file, "string data", overwrite=True)
                            mock_file.assert_called()
                            mock_replace.assert_called()

    def test_save_file_json_exception_cleanup_file_exists(self):
        """Test save_file_json exception cleanup when output file exists."""
        test_file = self.temp_path / "test.json"

        with patch("dpn_pyutils.file.get_random_string", return_value="random123"):
            with patch("dpn_pyutils.file.get_valid_file", return_value=test_file):
                with patch("builtins.open", side_effect=OSError("Write error")):
                    with patch.object(Path, "exists", return_value=True):
                        with patch.object(Path, "unlink") as mock_unlink:
                            with self.assertRaises(FileSaveError):
                                save_file_json(test_file, {"test": "data"}, overwrite=True)
                            mock_unlink.assert_called_once()


if __name__ == "__main__":
    unittest.main()
