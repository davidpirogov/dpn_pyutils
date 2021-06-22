from dpn_pyutils.exceptions import FileOperationError
import pytest
import datetime as dt
from pathlib import Path
from colorama import Fore

from dpn_pyutils import cli
from dpn_pyutils import common
from dpn_pyutils import file

#
# Module tests: cli
#

def esc(code):
    return f'\033[{code}m'


def test_color_output():
    """
    Tests the string output based on the ASCII terminal color codes
    https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
    """

    text = "This text should be red"

    red_fore_text = cli.color_t(text, Fore.RED)
    known_red_fore_text = "{}{}{}{}".format(esc(31), esc(49), text, esc(0))

    # print(bytes(red_fore_text, 'utf8'))
    # print(bytes(known_red_fore_text, 'utf8'))

    assert red_fore_text == known_red_fore_text


#
# Module tests: common
#

def get_logging_config():
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "logging_project_name": "dpn-pyutils-test-project-name",
        "formatters": {
            "default": {
                "class": "logging.Formatter",
                "format": "%(asctime)s.%(msecs)03d %(name)s %(levelname)-8s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers":{
            "default": {
                "level": "DEBUG",
                "handlers": [ "console" ],
                "propagate": False
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": [ "console" ]
        }
    }


def test_logging_initialization():

    logging_config = get_logging_config()
    common.initialize_logging(logging_config)

    log = common.get_logger("test-module")
    log.debug("Testing log debug output")

#
# Module tests: file
#

def get_test_data() -> dict:
    return {
        "test data": [
            "data1",
            "data2",
            "data3"
        ],
        "timestamp": dt.datetime.now()
    }

def test_save_file_text():

    save_path = Path("test.txt")

    # Save the file and and test that it's been saved
    file.save_file_text(save_path, get_test_data())
    assert save_path.exists()

    with pytest.raises(FileOperationError) as e:
        # Try to save a second time and it should fail
        file.save_file_text(save_path, get_test_data())

    # Clean up
    save_path.unlink()


def test_save_file_json():

    save_path = Path("test.json")

    # Save the file and and test that it's been saved
    file.save_file_json(save_path, get_test_data())
    assert save_path.exists()

    with pytest.raises(FileOperationError) as e:
        # Try to save a second time and it should fail
        file.save_file_json(save_path, get_test_data())

    # Clean up
    save_path.unlink()

if __name__ == "__main__":

    print("Running test_color_output")
    test_color_output()

    print("Running test_logging_initialization")
    test_logging_initialization()

    print("Running test_save_file_text")
    test_save_file_text()

    print("Running test_save_file_json")
    test_save_file_json()
