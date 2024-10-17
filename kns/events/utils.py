"""
Utility functions for the `events` app.
"""

from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ValidationError,
)


# Validator helper to DRY
def get_min_max_validator(min_len, max_len, min_msg, max_msg):
    """
    Return a list of validators for minimum and maximum length.

    Parameters
    ----------
    min_len : int
        Minimum length allowed for the field.
    max_len : int
        Maximum length allowed for the field.
    min_msg : str
        Error message if the input is shorter than the minimum length.
    max_msg : str
        Error message if the input is longer than the maximum length.

    Returns
    -------
    list
        A list containing MinLengthValidator and MaxLengthValidator.
    """
    return [
        MinLengthValidator(
            min_len,
            message=min_msg,
        ),
        MaxLengthValidator(
            max_len,
            message=max_msg,
        ),
    ]


# Image validation for file size
def validate_image(image):
    """
    Validate the file size of an image to ensure it does not exceed 500 KB.

    Parameters
    ----------
    image : ImageFieldFile
        The image file to validate.

    Raises
    ------
    ValidationError
        If the image size exceeds the 500 KB limit.
    """
    file_size = image.file.size
    limit_kb = 500  # 500KB limit
    if file_size > limit_kb * 1024:
        raise ValidationError(f"Max size of file is {limit_kb} KB")
