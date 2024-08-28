"""
Custom tags for the `profiles` app.
"""

from django import template

register = template.Library()


@register.filter
def get_nth_element(lst, index):
    """
    Return the element at the specified index from the given list.

    This custom template filter retrieves the element at the `index` position from the `lst`.
    If the index is out of range, not a valid integer, or if the list is `None`, it returns `None`.

    Parameters
    ----------
    lst : list
        The list from which the element is to be retrieved.
    index : int or str
        The index of the element to retrieve. This can be provided as an integer or a string
        that can be converted to an integer.

    Returns
    -------
    object or None
        The element at the specified index, or `None` if the index is invalid or the list is empty.
    """
    try:
        if index is None:
            return None
        return lst[int(index)]
    except (IndexError, ValueError, TypeError):
        return None
