import decimal
import datetime as dt
from typing import List
import toml
import re
import orjson as json
from io import StringIO
import csv

from pathlib import Path

from .common import get_logger
from .crypto import get_random_string
from .exceptions import FileOpenError, FileSaveError


def json_serialiser(obj) -> str:
    """ Serialises known types to their string versions """

    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    raise TypeError("Type '{}' is not JSON serializable".format(type(obj)))


def read_file_json(json_file_path) -> any:
    """
    Accepts a Path object to a JSON file and read it into a dict or array structure
    """
    if not json_file_path.exists():
        raise FileNotFoundError(json_file_path, "File with path '{}' does not exist!".format(
            json_file_path.absolute()))

    try:
        # Must include 'b' option for reading orjson
        file_bytes = __try_read_file(json_file_path, use_binary_read=True)
        return json.loads(file_bytes)
    except OSError as e:
        raise FileOpenError(json_file_path, "Error while trying to read file '{}' as JSON".format(
            json_file_path.absolute()), e)


def read_file_text(text_file_path: Path) -> str:
    """
    Accepts a path object to a file and reads it as text
    """

    if not text_file_path.exists():
        raise FileNotFoundError(text_file_path, "File with path '{}' does not exist!".format(
            text_file_path.absolute()))

    try:
        file_bytes = __try_read_file(text_file_path)
        return str(file_bytes)
    except OSError as e:
        raise FileOpenError(text_file_path, "Error while trying to read file '{}' as text".format(
            text_file_path.absolute()), e)


def read_file_toml(toml_file_path: Path) -> dict:
    """
    Accepts a path object to a file and reads it as a TOML configuration file
    """

    file_contents = read_file_text(toml_file_path)
    return toml.loads(file_contents)


def read_file_csv(csv_file_path: Path, delimiter: str = ",", quote_char: str = "\"") -> List:
    """
    Accepts a path object to a file and attempts to read it as a CSV file with optional
    delimeter and quote character specifications
    """

    file_contents = read_file_text(csv_file_path)
    csv_fp = StringIO(file_contents)
    csv_contents = []
    reader = csv.reader(csv_fp, delimiter=delimiter, quotechar=quote_char)
    for row in reader:
        csv_contents.append(row)

    return csv_contents

def __try_read_file(file_path: Path, use_binary_read=False) -> bytes:
    """
    Read file content into an array of bytes
    """

    file_mode = "r"
    if use_binary_read:
        file_mode += "b"

    with open(file_path.absolute(), file_mode) as f:
        return f.read()


def save_file_text(text_file_path: Path, data: any, overwrite=False) -> None:
    """
    Accepts a Path object to a text file and writes the data to the file
    """
    if not __check_save_file(text_file_path, overwrite):
        return

    try:
        text_serialised_data = str(data)
        __try_save_file(text_file_path, text_serialised_data)
    except OSError as e:
        raise FileSaveError(text_file_path, "Error while trying to save file '{}' as text".format(
            text_file_path.absolute()), e)


def save_file_json(json_file_path: Path, data: any, overwrite=False) -> None:
    """
    Accepts a Path object to a JSON file and writes a dict to a JSON structure
    """
    default_serializer_options = json.OPT_APPEND_NEWLINE | \
        json.OPT_INDENT_2 | \
        json.OPT_NAIVE_UTC | \
        json.OPT_SERIALIZE_NUMPY | \
        json.OPT_SERIALIZE_UUID | \
        json.OPT_OMIT_MICROSECONDS | \
        json.OPT_STRICT_INTEGER

    save_file_json_opts(json_file_path, data, overwrite,
                        default_serializer_options)


def save_file_json_opts(json_file_path: Path, data: any, overwrite=False, serializer_opts=None) -> None:
    """
    Accepts a Path object to a JSON file and writes a dict to a JSON structure
    """

    if not __check_save_file(json_file_path, overwrite):
        return

    try:
        json_formatted_data = json.dumps(data,
                                         option=serializer_opts,
                                         default=json_serialiser)

        # Must include 'b' option for writing orjson
        __try_save_file(json_file_path, json_formatted_data, use_binary_write=True)
    except OSError as e:
        raise FileSaveError(json_file_path, "Error while trying to save file '{}' as JSON".format(
            json_file_path.absolute()), e)


def __try_save_file(json_file_path: Path, data: any, use_binary_write=False) -> None:
    """
    NOTE: Do not call this method directly. Use associated save_file_* functions
    """

    # Write the output to a random file and move into the correct location
    random_file_name = get_random_string()
    output_file_path = get_valid_file(json_file_path.parent, random_file_name)

    try:
        file_mode = "w"
        if use_binary_write:
            file_mode += "b"

        with open(output_file_path.absolute(), file_mode) as write_file:
            # If we are using a binary write mode and the data is not in the right
            # format (byte array), then convert it into a byte array before writing
            if use_binary_write and type(data) != bytes:
                write_file.write(bytes(data, 'utf8'))
            else:
                write_file.write(data)

        output_file_path.replace(json_file_path)
    except:
        # Clean up our temporary file since there was an error in writing the output
        # We do not need to unlink on success because the file is replaced
        if output_file_path.exists():
            output_file_path.unlink()

        # Re-raise the exception
        raise



def __check_save_file(file_path: Path, overwrite: bool) -> bool:
    """
    Checks if a file can be overwritten based on the supplied path and overwrite flag
    """
    if file_path.exists() and not overwrite:
        raise FileSaveError(
            file_path, "File '{}' exists and the overwrite flag is not set to True!".format(file_path.absolute()))

    return True


def get_valid_file(location_dir: Path, file_name: str, use_timestamp=False) -> Path:
    """
    Gets an output filename for a file in a path. If the file exists, it will
    append a "_x" where x is a number

    Optionally, add a timestamp to the file name instead of a sequential number
    """

    check_loop = 0
    while True:
        check_loop += 1
        if use_timestamp:
            file_name = append_value_to_filename(
                file_name, "_{}".format(int(dt.datetime.now().timestamp())))

        candidate_file_name = Path(location_dir.absolute(), file_name)
        if not candidate_file_name.exists():
            break
        else:
            file_name = append_value_to_filename(
                file_name, "_{}".format(check_loop))

    return candidate_file_name


def append_value_to_filename(file_name: str, value_to_insert: str):
    """ Inserts a value between the filename and the extension """

    filename_parts = file_name.split('.')
    if len(filename_parts) <= 1:
        return "{}{}".format(file_name, value_to_insert)
    else:
        return "{}{}.{}".format(
            '.'.join(filename_parts[0:(len(filename_parts) - 1)]),
            value_to_insert,
            '.'.join(
                filename_parts[len(filename_parts) - 1:len(filename_parts)])
        )


def get_timestamp_formatted_file_dir(parent_data_dir: Path, timestamp: dt.datetime, resolution="HOUR", create_dir=False) -> Path:
    """
    Creates and/or returns a formatted file directory based on the parent dir, the timestmap, and resolution
    """

    # Format numbers to have leading zeroes
    timestamp_blocks = (timestamp.strftime("%Y"),
                        timestamp.strftime("%m"),
                        timestamp.strftime("%d"),
                        timestamp.strftime("%H"),
                        timestamp.strftime("%M"),
                        timestamp.strftime("%S"))

    formatted_dir_prefix = ""

    # Notes:
    #
    # Reason for doing "YYYY-mm-dd" is that the total number of file system objects
    # will not exceed un-manageable levels (e.g. >10,000) in one directory.
    #
    # At the hour and minute level, every day is partitioned hourly, minute, and second dirs
    # as the number of file system objects can grow very large.
    #
    # If the number of file system objects is expected to be extremely large, use a hash-formatted
    # file directory structure, rather than this timestamp formatted file directory structure

    if resolution == "YEAR":
        formatted_dir_prefix = "/{}".format(*timestamp_blocks)
    elif resolution == "MONTH":
        formatted_dir_prefix = "/{}-{}".format(*timestamp_blocks)
    elif resolution == "DAY":
        formatted_dir_prefix = "/{}-{}-{}".format(*timestamp_blocks)
    elif resolution == "HOUR":
        formatted_dir_prefix = "/{}-{}-{}/{}".format(*timestamp_blocks)
    elif resolution == "MINUTE":
        formatted_dir_prefix = "/{}-{}-{}/{}/{}".format(*timestamp_blocks)
    else:
        formatted_dir_prefix = "/{}-{}-{}/{}/{}/{}".format(*timestamp_blocks)

    formatted_full_path = Path(
        "{}/{}".format(parent_data_dir, formatted_dir_prefix))

    if create_dir and not formatted_full_path.exists():
        get_logger(__name__).debug("Full path for this file does not exist. Creating '{}'".format(
            formatted_full_path.absolute()))
        formatted_full_path.mkdir(parents=True)

    return formatted_full_path


def get_cachekey(cache_ttl: int, timestamp: dt.datetime = dt.datetime.now()) -> str:
    """
    Gets a cachekey tag (string) based on the current time and format
    """

    cachekey_timestamp_format = get_timestamp_format_by_ttl_seconds(cache_ttl)

    return timestamp.strftime(cachekey_timestamp_format)


def get_timestamp_format_by_ttl_seconds(ttl_value: int) -> str:
    """
    Calculates the precision of the timestamp format required based on the TTL
    For example:
        if TTL is 3600 seconds (1hr) then return "%Y-%m-%d-%H0000"
        if TTL is 600 seconds (10 mins) then return "%Y-%m-%d-%H%M00"
        if TTL is 35 seconds (35 secs) then return "%Y-%m-%d-%H%M%S"
    """

    if ttl_value >= 86400:
        # Greater than one day, return a day timestamp
        return "%Y-%m-%d-000000"

    elif ttl_value >= 3600:
        # Greater than one hour, return an hour-based timestamp
        return "%Y-%m-%d-%H0000"

    elif ttl_value >= 60:
        # Greater than a minute, return a minute-based timestamp
        return "%Y-%m-%d-%H%M00"

    else:
        # Return a second-based timestmap
        return "%Y-%m-%d-%H%M%S"


def get_file_list_from_dir(parent_dir: Path, file_mask: str = "*") -> list:
    """
    Recursively gets a list of files in a Path directory with the specified name mask
    and return absolute string paths for files
    """
    get_logger(__name__).debug("Iterating for files in '{}'".format(parent_dir.absolute()))
    src_glob = parent_dir.rglob(file_mask)
    src_files = [str(f.absolute()) for f in src_glob if f.is_file()]
    get_logger(__name__).debug("Iterated and found {} files in '{}'".format(len(src_files), parent_dir.absolute()))

    return src_files


def extract_timestamp_from_snapshot_key(snapshot_key: str) -> dt.datetime:
    """
    Extracts the timespan from a snapshot key, such as from trending-snapshot-2021-01-01-143546
    """

    extraction_regex = r"(.*)([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})([0-9]{2})([0-9]{2})"
    matches = re.match(pattern=extraction_regex, string=snapshot_key)
    (
        _,
        year,
        month,
        day,
        hour,
        minute,
        second
    ) = matches.groups()

    return dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), 0)


def prepare_timestamp_datapath( data_dir: Path, timestamp: dt.datetime, data_dir_resolution="DAY",
                                data_file_timespan=3600, data_file_prefix="") -> Path:
    """
    Prepares a data path for data to be stored based on time frames, with an optional prefix

    """

    formatted_data_dir = get_timestamp_formatted_file_dir(data_dir, timestamp, data_dir_resolution)

    formatted_data_key = "{}{}".format(data_file_prefix, get_cachekey(data_file_timespan, timestamp))

    datapath_file = Path("{}/{}.json".format(formatted_data_dir, formatted_data_key))

    return datapath_file
