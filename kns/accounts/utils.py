"""
Utility functions for password comparison and URL safety checks.

This module provides helper functions to compare passwords.
"""


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
