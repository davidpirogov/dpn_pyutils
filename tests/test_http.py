import unittest

from dpn_pyutils.http import is_url


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
        self.assertFalse(is_url(url))  # type: ignore

    def test_is_url_malformed(self):
        # Test with a malformed URL
        url = "htp:/example"
        self.assertFalse(is_url(url))

    def test_is_url_value_error_exception(self):
        # Test with a URL that raises ValueError during parsing
        # This tests the exception handling path in is_url function
        url = "http://[invalid-url"
        self.assertFalse(is_url(url))

    def test_is_url_with_query_parameters(self):
        # Test with valid URLs containing query parameters
        valid_urls = [
            "https://www.example.com?param=value",
            "https://www.example.com/path?param1=value1&param2=value2",
            "http://localhost:8080/api?token=abc123",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_url(url))

    def test_is_url_with_fragments(self):
        # Test with valid URLs containing fragments
        valid_urls = [
            "https://www.example.com#section1",
            "https://www.example.com/path#top",
            "http://localhost:8080/page#anchor",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_url(url))

    def test_is_url_various_schemes(self):
        # Test with various valid URL schemes
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "ftp://example.com",
            "ftps://example.com",
            "file:///path/to/file",
            "mailto:user@example.com",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_url(url))

    def test_is_url_edge_cases(self):
        # Test edge cases that might cause issues
        edge_cases = [
            "a" * 1000,  # Very long string
            "http://",  # Just scheme
            "://example.com",  # Missing scheme
            "http:///path",  # Triple slash
            "https://example.com:8080",  # With port
            "https://user@example.com",  # With user info
        ]

        for url in edge_cases:
            with self.subTest(url=url):
                # Should not raise an exception, should return bool
                result = is_url(url)
                self.assertIsInstance(result, bool)
