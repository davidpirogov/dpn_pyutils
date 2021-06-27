import random
import hashlib
import time
import base64

from .exceptions import CryptoInvalidArgumentsError

ALPHA_CHARS = "{}{}".format(
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
)

NUM_CHARS = "0123456789"

ALPHA_NUM_CHARS = "{}{}".format(
    ALPHA_CHARS,
    NUM_CHARS
)

def get_random_number(min: int, max: int) -> int:
    """
    Gets a random number between min and max inclusive.
    """
    rand = random.Random()
    return rand.randint(min, max)


def get_random_string(length: int = 10, allowed_characters: str = ALPHA_NUM_CHARS) -> str:
    """
    Gets a randomly generated alphanumeric string with the supplied length
    """

    allowed_characters_len = len(allowed_characters)
    if length <= allowed_characters_len:
        return __get_rand_str(length, allowed_characters)

    result = ""
    for i in range(0, length, allowed_characters_len):

        # Ensure we pick the right number of characters for the
        # last block
        block_length = allowed_characters_len
        if length < (i + block_length):
            block_length = length - i

        result += __get_rand_str(block_length, allowed_characters)

    return result


def __get_rand_str(str_length: int, allowed_characters: str) -> str:
    """
    NOTE: Do not use this method directly. Use get_random_string()
    """

    t1 = time.time_ns()
    if str_length > len(allowed_characters):
        raise CryptoInvalidArgumentsError(
            message="""
            Invalid arguments (length={}, allowed_characters='{}', length={}) passed to __get_rand_str.
            Do not call this method directly or ensure that str_length is less than or equal to
            the length of allowed_characters
            """.format(str_length, allowed_characters, len(allowed_characters)))

    rand = random.Random()
    t2 = time.time_ns()

    rand.seed(
        hashlib.sha256(
            "{}{}{}".format(
                t1,
                rand.getstate(),
                t2,
            )
            .encode('utf8')
        )
        .digest()
    )

    return "".join(rand.choice(allowed_characters) for i in range(str_length))



def encode_base64(plain_string: str) -> str:
    """
    Encodes a URL-safe base64 version of a plain string
    """
    return base64.urlsafe_b64encode(plain_string)


def decode_base64(encoded_string: str) -> str:
    """
    Decodes a URL-safe base64 version of an encoded string
    """
    return base64.urlsafe_b64decode(encoded_string)
