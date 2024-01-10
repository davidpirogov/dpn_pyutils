import unittest

from src.dpn_pyutils.crypto import (
    decode_base64,
    encode_base64,
    get_random_number,
    get_random_string,
)


class CryptoTestCase(unittest.TestCase):
    def test_get_random_number(self):
        # Test if the generated random number is within the specified range
        min_value = 1
        max_value = 10
        random_number = get_random_number(min_value, max_value)
        self.assertGreaterEqual(random_number, min_value)
        self.assertLessEqual(random_number, max_value)

    def test_get_random_string(self):
        # Test if the generated random string has the correct length and contains only allowed characters
        length = 10
        allowed_characters = "abc123"
        random_string = get_random_string(length, allowed_characters)
        self.assertEqual(len(random_string), length)
        self.assertTrue(all(char in allowed_characters for char in random_string))

    def test_encode_base64(self):
        # Test if the base64 encoding is correct
        plain_string = "Hello, World!"
        encoded_string = encode_base64(plain_string)
        self.assertEqual(encoded_string, "SGVsbG8sIFdvcmxkIQ==")

    def test_decode_base64(self):
        # Test if the base64 decoding is correct
        encoded_string = "SGVsbG8sIFdvcmxkIQ=="
        decoded_string = decode_base64(encoded_string)
        self.assertEqual(decoded_string, "Hello, World!")


if __name__ == "__main__":
    unittest.main()
