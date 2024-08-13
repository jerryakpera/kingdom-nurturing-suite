"""
Utility functions for password comparison and URL safety checks.

This module provides helper functions to compare passwords and check if a URL
is safe for redirection based on allowed hosts.
"""

from urllib.parse import urlparse


def compare_passwords(password1, password2):
    """
    Compare two passwords for equality.

    Parameters
    ----------
    password1 : str
        The first password to compare.
    password2 : str
        The second password to compare.

    Returns
    -------
    bool
        True if the passwords are the same, False otherwise.
    """
    return password1 == password2


def is_safe_url(url, allowed_hosts):
    """
    Check if a URL is safe for redirection based on allowed hosts.

    Parameters
    ----------
    url : str
        The URL to check.
    allowed_hosts : list of str
        A list of allowed hosts for URL redirection.

    Returns
    -------
    bool
        True if the URL's netloc is in the allowed hosts, False otherwise.
    """
    if url is None:
        return False

    # Parse the URL and check if it's within allowed hosts
    parsed_url = urlparse(url)
    return parsed_url.netloc in allowed_hosts
