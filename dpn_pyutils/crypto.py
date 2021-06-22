import random
import hashlib
import time
import base64

def get_random_number(min: int, max: int) -> int:
    """
    Gets a random number between min and max inclusive.
    """
    rand = random.Random()
    return rand.randint(min, max)


def get_random_string(length: int = 10, allowed_characters="abcdefghijklmnopqrstuvwxyz"
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") -> int:
    """
    Gets a randomly generated alphanumeric string with the supplied length
    """

    t1 = time.time_ns()
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

    return "".join(random.choice(allowed_characters) for i in range(length))


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
