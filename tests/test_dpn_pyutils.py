import pytest
import datetime as dt
from pathlib import Path
from colorama import Fore
import unittest

from src.dpn_pyutils import cli
from src.dpn_pyutils import crypto
from src.dpn_pyutils import common
from src.dpn_pyutils import file
from src.dpn_pyutils import money
from src.dpn_pyutils.exceptions import FileOperationError



class TestDpnPyUtils(unittest.TestCase):
    """
    https://docs.python.org/3.8/library/unittest.html#basic-example
    """

    #
    # Module tests: cli
    #

    def esc(self, code:int) -> str:
        return "\033[{}m".format(code)


    def test_color_output(self):
        """
        Tests the string output based on the ASCII terminal color codes
        https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
        """

        text = "This text should be red"

        red_fore_text = cli.color_t(text, Fore.RED)
        known_red_fore_text = "{}{}{}{}".format(self.esc(31), self.esc(49), text, self.esc(0))

        # print(bytes(red_fore_text, 'utf8'))
        # print(bytes(known_red_fore_text, 'utf8'))

        assert red_fore_text == known_red_fore_text

    def test_args_process(self):

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
    def test_crypto_output(self):

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

        rnd_num_1 = crypto.get_random_number(0, 1)
        assert (rnd_num_1 >= 0) and (rnd_num_1 <= 1)

        rnd_num_2 = crypto.get_random_number(150, 150)
        assert (rnd_num_2 >= 150) and (rnd_num_2 <= 150)

        rnd_num_3 = crypto.get_random_number(-120, -120)
        assert (rnd_num_3 >= -120) and (rnd_num_3 <= -120)


    #
    # Module tests: common
    #

    def get_logging_config(self):
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
                    "level": "TRACE",
                    "formatter": "default",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers":{
                "default": {
                    "level": "TRACE",
                    "handlers": [ "console" ],
                    "propagate": False
                },
            },
            "root": {
                "level": "TRACE",
                "handlers": [ "console" ]
            }
        }


    def test_logging_initialization(self):

        logging_config = self.get_logging_config()
        common.initialize_logging(logging_config)

        log = common.get_logger("test-module")
        log.debug("Testing log debug output")
        log.trace("Testing log trace output")

    #
    # Module tests: file
    #

    def get_test_data(self) -> dict:
        return {
            "test data": [
                "data1",
                "data2",
                "data3"
            ],
            "timestamp": dt.datetime.now()
        }

    def test_save_file_text(self):

        save_path = Path("test.txt")

        # Save the file and and test that it's been saved
        file.save_file_text(save_path, self.get_test_data())
        assert save_path.exists()

        with pytest.raises(FileOperationError) as e:
            # Try to save a second time and it should fail
            file.save_file_text(save_path, self.get_test_data())

        # Clean up
        save_path.unlink()


    def test_save_file_json(self):

        save_path = Path("test.json")

        # Save the file and and test that it's been saved
        file.save_file_json(save_path, self.get_test_data())
        assert save_path.exists()

        with pytest.raises(FileOperationError) as e:
            # Try to save a second time and it should fail
            file.save_file_json(save_path, self.get_test_data())

        # Clean up
        save_path.unlink()


    def test_file_timestamps_format(self):

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

    def test_format_currency(self):

        # Test float formats
        assert "<$0.000001" == money.format_currency_market_display_float(0.000_000_1)
        assert "<-$0.000001" == money.format_currency_market_display_float(-0.000_000_5)

        assert "$0.0047" == money.format_currency_market_display_float(0.0047)
        assert "-$0.002" == money.format_currency_market_display_float(-0.002)

        assert "£0.53" == money.format_currency_market_display_float(0.53, currency_symbol="£")
        assert "-£0.82" == money.format_currency_market_display_float(-0.82, currency_symbol="£")

        assert "$5.31" == money.format_currency_market_display_float(5.31)
        assert "-$991.53" == money.format_currency_market_display_float(-991.530_001)

        assert "$1.00k" == money.format_currency_market_display_float(1000)
        assert "-$981.65k est." == money.format_currency_market_display_float(-981_652.65, suffix=" est.")

        assert "$3.2M" == money.format_currency_market_display_float(3_244_123)
        assert "-$932.7M" == money.format_currency_market_display_float(-932_735_000)

        assert "$4.5B" == money.format_currency_market_display_float(4_541_000_000)
        assert "-$983.8B" == money.format_currency_market_display_float(-983_835_000_000)

        assert "$1.2T" == money.format_currency_market_display_float(1_201_000_000_000)
        assert "-$3.6T" == money.format_currency_market_display_float(-3_587_000_000_000) # Bank round up on >x.5

