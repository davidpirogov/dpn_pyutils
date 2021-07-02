from urllib import urlparse

def is_url(url: str):
    """ 
    Code from https://stackoverflow.com/a/52455972 
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
