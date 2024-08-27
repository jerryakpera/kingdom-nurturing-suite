"""
Util functions for the `core` app.
"""


def log_this(item, sign="*"):  # pragma: no cover
    """
    Log an item with a specified visual separator.

    Parameters
    ----------
    item : str
        The item or message to be logged.
    sign : str, optional
        The character used to create the separator lines. Defaults to '*'.

    Returns
    -------
    None
        This function does not return a value. It prints the item and separator to the console.
    """

    print("")
    print(sign * 30)
    print(item)
    print(sign * 30)
    print("")
