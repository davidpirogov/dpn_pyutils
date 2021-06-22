from urllib import urlparse

# TODO: Move to library.http module
def is_url(url):
    """ Code from https://stackoverflow.com/a/52455972 """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
