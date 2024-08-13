from urllib.parse import urlparse


def compare_passwords(password1, password2):
    return password1 == password2


def is_safe_url(url, allowed_hosts):
    """Check if a URL is safe for redirection."""
    if url is None:
        return False

    # Parse the URL and check if it's within allowed hosts
    parsed_url = urlparse(url)
    return parsed_url.netloc in allowed_hosts
