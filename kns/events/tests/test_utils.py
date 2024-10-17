from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from kns.events.utils import get_min_max_validator, validate_image


class TestGetMinMaxValidator(TestCase):
    def test_valid_length(self):
        """
        Test if the validators allow valid input length.
        """
        validators = get_min_max_validator(5, 10, "Too short", "Too long")
        test_value = "valid"

        # Should not raise ValidationError for valid input
        for validator in validators:
            validator(test_value)

    def test_min_length_violation(self):
        """
        Test if the validators raise ValidationError for input that is too short.
        """
        validators = get_min_max_validator(5, 10, "Too short", "Too long")
        test_value = "tiny"

        with self.assertRaisesMessage(ValidationError, "Too short"):
            validators[0](test_value)  # MinLengthValidator

    def test_max_length_violation(self):
        """
        Test if the validators raise ValidationError for input that is too long.
        """
        validators = get_min_max_validator(
            5,
            10,
            "Too short",
            "Too long",
        )
        test_value = "waytoolonginput"

        with self.assertRaisesMessage(ValidationError, "Too long"):
            validators[1](test_value)  # MaxLengthValidator


class TestValidateImage(TestCase):
    def test_validate_image_with_valid_size(self):
        """
        Test that validate_image allows images below the size limit.
        """
        # Mock image with a file size below 500 KB
        mock_image = Mock()
        mock_image.file.size = 400 * 1024  # 400 KB

        try:
            validate_image(mock_image)
        except ValidationError:
            self.fail("validate_image raised ValidationError unexpectedly!")

    def test_validate_image_with_invalid_size(self):
        """
        Test that validate_image raises ValidationError for images above the size limit.
        """
        # Mock image with a file size above 500 KB
        mock_image = Mock()
        mock_image.file.size = 600 * 1024  # 600 KB

        with self.assertRaisesMessage(ValidationError, "Max size of file is 500 KB"):
            validate_image(mock_image)
