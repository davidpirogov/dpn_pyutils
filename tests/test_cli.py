import unittest

from colorama import Back, Fore

from src.dpn_pyutils.cli import (
    color_format_string,
    color_t,
    color_var,
    color_var_fore,
    color_var_fore_back,
    get_arg,
    parse_cli_args,
)


class TestCLIMethods(unittest.TestCase):
    """
    Tests CLI methods
    """

    def test_color_t(self):
        self.assertEqual(
            color_t("Hello", Fore.RED),
            "\x1b[31m\x1b[49mHello\x1b[0m",
        )

    def test_color_var_fore(self):
        self.assertEqual(
            color_var_fore("Label", "Value", Fore.GREEN),
            "\x1b[39m\x1b[49mLabel\x1b[0m \x1b[32m\x1b[49mValue\x1b[0m",
        )

    def test_color_var(self):
        self.assertEqual(
            color_var("Label", Fore.BLUE, "Value", Back.YELLOW),
            "\x1b[34m\x1b[49mLabel\x1b[0m \x1b[43m\x1b[49mValue\x1b[0m",
        )

    def test_color_var_fore_back(self):
        self.assertEqual(
            color_var_fore_back(
                "Label", Fore.RED, Back.WHITE, "Value", Fore.GREEN, Back.BLUE
            ),
            "\x1b[31m\x1b[47mLabel\x1b[0m \x1b[32m\x1b[44mValue\x1b[0m",
        )

    def test_color_format_string(self):
        self.assertEqual(
            color_format_string("Hello", Fore.CYAN, Back.MAGENTA),
            "\x1b[36m\x1b[45mHello\x1b[0m",
        )

    def test_get_arg(self):
        args = [{"name": "John"}, {"age": "30"}]
        self.assertEqual(get_arg("name", args), "John")
        self.assertEqual(get_arg("age", args), "30")

    def test_parse_cli_args(self):
        args = ["--name", "John", "--age", "30"]

        self.assertListEqual(parse_cli_args(args), [{"name": "John"}, {"age": "30"}])


if __name__ == "__main__":
    unittest.main()
