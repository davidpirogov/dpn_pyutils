import timeit

from dpn_pyutils import cli
from dpn_pyutils import crypto
from dpn_pyutils import common
from dpn_pyutils import file
from dpn_pyutils import money


def time_crypto_short_alphanum_string():
    short_alphanum_len = len(crypto.ALPHA_NUM_CHARS)
    s = crypto.get_random_string(length=short_alphanum_len, allowed_characters=crypto.ALPHA_CHARS)

def time_crypto_long_alphanum_string():
    short_alphanum_len = len(crypto.ALPHA_NUM_CHARS)
    long_alphanum_len = 2 * short_alphanum_len + 1
    s = crypto.get_random_string(length=long_alphanum_len, allowed_characters=crypto.ALPHA_CHARS)



if __name__ == "__main__":

    repeat_amount = 10000
    results = {
        "short_alphanum": timeit.timeit(stmt=time_crypto_short_alphanum_string, number=repeat_amount),
        "long_alphanum": timeit.timeit(stmt=time_crypto_long_alphanum_string, number=repeat_amount)
    }

    for r in results:
        print(r)
        print(results[r])
