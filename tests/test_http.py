import unittest

from src.dpn_pyutils.http import is_url


class TestHttp(unittest.TestCase):
    def test_is_url_valid(self):
        # Test with a valid URL
        url = "https://www.example.com"
        self.assertTrue(is_url(url))

    def test_is_url_invalid(self):
        # Test with an invalid URL
        url = "example.com"
        self.assertFalse(is_url(url))

    def test_is_url_empty(self):
        # Test with an empty URL
        url = ""
        self.assertFalse(is_url(url))

    def test_is_url_none(self):
        # Test with a None URL
        url = None
        self.assertFalse(is_url(url)) # type: ignore

if __name__ == '__main__':
    unittest.main()
