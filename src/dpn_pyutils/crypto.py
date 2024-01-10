import base64
import secrets
import string

ALPHA_CHARS = string.ascii_letters

NUM_CHARS = string.digits

ALPHA_NUM_CHARS = f"{ALPHA_CHARS}{NUM_CHARS}"



def get_random_number(min: int, max: int) -> int:
    """
    Gets a random number between min and max inclusive.
    """
    rand = secrets.SystemRandom()
    return rand.randint(min, max)


def get_random_string(
    length: int = 10, allowed_characters: str = ALPHA_NUM_CHARS
) -> str:
    """
    Gets a randomly generated alphanumeric string with the supplied length
    """
    return "".join(secrets.choice(allowed_characters) for i in range(length))


def encode_base64(plain_string: str) -> str:
    """
    Encodes a URL-safe base64 version of a plain string
    """
    return base64.urlsafe_b64encode(plain_string.encode("utf-8")).decode("utf-8")


def decode_base64(encoded_string: str) -> str:
    """
    Decodes a URL-safe base64 version of an encoded string
    """
    return base64.urlsafe_b64decode(encoded_string).decode("utf-8")
