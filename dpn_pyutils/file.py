import decimal
import datetime as dt
from pathlib import Path
import orjson as json

from .exceptions import FileOpenError, FileSaveError
from .crypto import get_random_string


def json_serialiser(obj):
    """ Serialises known types to their string versions """

    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return str(obj)

    raise TypeError("Type '{}' is not JSON serializable".format(type(obj)))


def read_file_json(json_file_path):
    """
    Accepts a Path object to a JSON file and read it into a JSON structure
    """
    if not json_file_path.exists():
        raise FileNotFoundError(json_file_path, "File with path '{}' does not exist!".format(
            json_file_path.absolute()))

    try:
        file_bytes = __try_read_file(json_file_path)
        return json.loads(file_bytes)
    except OSError as e:
        raise FileOpenError(json_file_path, "Error while trying to read file '{}' as JSON".format(
            json_file_path.absolute()), e)


def read_file_text(text_file_path):
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


def __try_read_file(file_path: Path) -> bytes:
    """
    Read file content into an array of bytes
    """
    # Must include 'b' option for orjson
    with open(file_path.absolute(), "rb") as f:
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
        __try_save_file(json_file_path, json_formatted_data)
    except OSError as e:
        raise FileSaveError(json_file_path, "Error while trying to save file '{}' as JSON".format(
            json_file_path.absolute()), e)


def __try_save_file(json_file_path: Path, data: any) -> bool:
    """
    NOTE: Do not call this method directly. Use associated save_file_* functions
    """

    # Write the output of our content to a random file first
    random_file_name = get_random_string()
    output_file_path = get_valid_file(json_file_path.parent, random_file_name)

    try:
        # Must include 'b' option for orjson
        with open(output_file_path.absolute(), "wb") as write_file:
            if type(data) == bytes:
                write_file.write(data)
            else:
                write_file.write(bytes(data, 'utf8'))

        output_file_path.replace(json_file_path)
    except:
        # Clean up our temporary file since there was an error in writing the output
        if output_file_path.exists():
            output_file_path.unlink()

        # Re-raise the exception
        raise

    return True


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
