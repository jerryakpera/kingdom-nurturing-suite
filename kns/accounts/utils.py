"""
Utility functions for password comparison and URL safety checks.

This module provides helper functions to compare passwords.
"""

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


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


def generate_verification_token(user):
    """
    Generate a verification token for a user.

    This token is used to verify the user's email address or to reset the password.

    Parameters
    ----------
    user : User
        The user object for whom the token is being generated.

    Returns
    -------
    str
        A token string that can be used to verify the user.
    """
    return default_token_generator.make_token(user)


def verify_token(user, token):
    """
    Verify a token for a user.

    This function checks whether a given token is valid for a specific user.

    Parameters
    ----------
    user : User
        The user object associated with the token.
    token : str
        The token string to be verified.

    Returns
    -------
    bool
        True if the token is valid for the user, False otherwise.
    """
    return default_token_generator.check_token(user, token)


def decode_uid(uidb64):
    """
    Decode a base64 encoded user ID.

    This function decodes a URL-safe base64 encoded string to retrieve the user's ID.

    Parameters
    ----------
    uidb64 : str
        The base64 encoded string representing the user's ID.

    Returns
    -------
    str or None
        The decoded user ID as a string, or None if decoding fails.
    """
    if not uidb64:
        return None

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        return uid
    except (TypeError, ValueError, OverflowError):
        return None
