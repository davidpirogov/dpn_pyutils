from dpn_pyutils.exceptions import FileOperationError
import pytest
import datetime as dt
from pathlib import Path
from colorama import Fore

from dpn_pyutils import cli
from dpn_pyutils import crypto
from dpn_pyutils import common
from dpn_pyutils import file

from dpn_pyutils import money


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

def test_args_process():

    sample_args = ['--server-name', 'localhost:1234',
                   '--non-interactive', # Boolean True (exists)
                   '--random-location=A and B = -- and C',
                   '-x', '10',
                   '-f=True', # String literal "True", should NOT be coerced by default
                   '-d' # Boolean True (exists)
                   ]

    parsed_args = cli.parse_cli_args(sample_args)

    assert "localhost:1234" == cli.get_arg("server-name", parsed_args)
    assert True == cli.get_arg("non-interactive", parsed_args)
    assert "A and B = -- and C" == cli.get_arg("random-location", parsed_args)
    assert "10" == cli.get_arg("x", parsed_args)
    assert "True" == cli.get_arg("f", parsed_args)
    assert True == cli.get_arg("d", parsed_args)

#
# Module tests: crypto
#
def test_crypto_output():

    str_len1 = crypto.get_random_string(length=1)
    assert len(str_len1) == 1

    str_len5 = crypto.get_random_string(length=5)
    assert len(str_len5) == 5

    # Test the boundary between returning a direct random string
    # and building out a long random string from a set of smaller randoms
    # With crypto.NUM_CHARS (0->9) the len(NUM_CHARS) == 10. 
    # len-9 is direct random string, len-10 is direct random, len-11 is multi-string
    str_len_num_09 = crypto.get_random_string(length=9, allowed_characters=crypto.NUM_CHARS)
    str_len_num_10 = crypto.get_random_string(length=10, allowed_characters=crypto.NUM_CHARS)
    str_len_num_11 = crypto.get_random_string(length=11, allowed_characters=crypto.NUM_CHARS)
    assert len(str_len_num_09) == 9
    assert len(str_len_num_10) == 10
    assert len(str_len_num_11) == 11

    str_len200 = crypto.get_random_string(length=200, allowed_characters=crypto.NUM_CHARS)
    assert len(str_len200) == 200

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


def test_file_timestamps_format():

    assert "%Y-%m-%d-000000" == file.get_timestamp_format_by_ttl_seconds(100000)
    assert "%Y-%m-%d-000000" == file.get_timestamp_format_by_ttl_seconds(86400)

    assert "%Y-%m-%d-%H0000" == file.get_timestamp_format_by_ttl_seconds(15000)
    assert "%Y-%m-%d-%H0000" == file.get_timestamp_format_by_ttl_seconds(3600)

    assert "%Y-%m-%d-%H%M00" == file.get_timestamp_format_by_ttl_seconds(3000)
    assert "%Y-%m-%d-%H%M00" == file.get_timestamp_format_by_ttl_seconds(60)

    assert "%Y-%m-%d-%H%M%S" == file.get_timestamp_format_by_ttl_seconds(59)
    assert "%Y-%m-%d-%H%M%S" == file.get_timestamp_format_by_ttl_seconds(1)


#
#   Module tests: money
#

def test_format_currency():

    # Test float formats
    assert "<$0.000001" == money.format_currency_market_display_float(0.0000001)
    assert "<-$0.000001" == money.format_currency_market_display_float(-0.0000005)

    assert "$0.0047" == money.format_currency_market_display_float(0.0047)
    assert "-$0.002" == money.format_currency_market_display_float(-0.002)

    assert "£0.53" == money.format_currency_market_display_float(0.53, currency_symbol="£")
    assert "-£0.82" == money.format_currency_market_display_float(-0.82, currency_symbol="£")

    assert "$5.31" == money.format_currency_market_display_float(5.31)
    assert "-$991.53" == money.format_currency_market_display_float(-991.530001)

    assert "$1.00k" == money.format_currency_market_display_float(1000)
    assert "-$981.65k est." == money.format_currency_market_display_float(-981652.65, suffix=" est.")

    assert "$3.2M" == money.format_currency_market_display_float(3244123)
    assert "-$932.7M" == money.format_currency_market_display_float(-932735000)

    assert "$4.5B" == money.format_currency_market_display_float(4541000000)
    assert "-$983.8B" == money.format_currency_market_display_float(-983835000000)

    assert "$1.2T" == money.format_currency_market_display_float(1201000000000)
    assert "-$3.6T" == money.format_currency_market_display_float(-3587000000000) # Bank round up on >x.5

if __name__ == "__main__":

    import better_exceptions
    better_exceptions.hook()

    print("Running test_color_output")
    test_color_output()

    print("Running test_args_process")
    test_args_process()

    print("Running test_logging_initialization")
    test_logging_initialization()

    print("Running test_save_file_text")
    test_save_file_text()

    print("Running test_save_file_json")
    test_save_file_json()

    print("Running test_file_timestamps")
    test_file_timestamps_format()

    print("Running test_format_currency")
    test_format_currency()

    print("Running test_crypto_output")
    test_crypto_output()
