"""
Forms for handling user authentication and password management.
"""

from django import forms
from django.forms.widgets import EmailInput, PasswordInput
from django.utils.translation import gettext_lazy as _

from .utils import compare_passwords


class ChangePasswordForm(forms.Form):
    """
    Form for changing a user's password.
    """

    current_password = forms.CharField(
        strip=False,
        required=True,
        label="Current password",
        widget=forms.PasswordInput(
            attrs={
                "autofocus": True,
                "autocomplete": "off",
                "id": "current_password",
                "name": "current_password",
            }
        ),
    )

    new_password = forms.CharField(
        strip=False,
        required=True,
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "id": "new_password",
                "autocomplete": "off",
                "name": "new_password",
            }
        ),
    )

    confirm_new_password = forms.CharField(
        strip=False,
        required=True,
        label="Confirm new password",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "off",
                "id": "confirm_new_password",
                "name": "confirm_new_password",
            }
        ),
    )

    def clean(self):
        """
        Validate the form data.

        This method checks if the new password is similar to the current password
        and whether the new password and confirmation password match. Adds errors
        to the form if validation fails.

        Returns
        -------
        dict
            The cleaned data after validation.
        """
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if current_password and new_password:
            if compare_passwords(current_password, new_password):
                self.add_error(
                    "new_password",
                    "New password cannot be similar to the current password.",
                )

        if new_password != confirm_new_password:
            self.add_error(
                "confirm_new_password",
                "Confirm new password must match your new password",
            )

        return cleaned_data


class LoginForm(forms.Form):
    """
    Form for user login.
    """

    email = forms.EmailField(
        required=True,
        widget=EmailInput(
            attrs={
                "id": "email",
                "name": "email",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        widget=PasswordInput(
            attrs={
                "id": "password",
                "name": "password",
            }
        ),
    )


class SetPasswordForm(forms.Form):
    """
    Form for setting a new password.
    """

    new_password = forms.CharField(
        required=True,
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "id": "new_password",
                "name": "new_password",
            }
        ),
    )

    confirm_password = forms.CharField(
        required=True,
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "id": "confirm_password",
                "name": "confirm_password",
            }
        ),
    )

    def clean(self):
        """
        Validate the form data.

        This method checks that the new password meets minimum length requirements
        and that both new password fields match. Adds errors to the form if validation
        fails.

        Returns
        -------
        dict
            The cleaned data after validation.
        """
        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if len(new_password) < 8:
            self.add_error(
                "new_password", "Your password must be at least 8 characters"
            )

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", "The new passwords do not match.")

        return self.cleaned_data
