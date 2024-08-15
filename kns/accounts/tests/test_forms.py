from django.test import TestCase

from kns.custom_user.models import User

from ..forms import ChangePasswordForm, LoginForm, SetPasswordForm


class ChangePasswordFormTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.form_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        }

    def test_valid_form(self):
        form = ChangePasswordForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_new_password_similar_to_current(self):
        self.form_data["new_password"] = "oldpassword"

        form = ChangePasswordForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)

    def test_passwords_do_not_match(self):
        self.form_data["confirm_new_password"] = "mismatch"

        form = ChangePasswordForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("confirm_new_password", form.errors)


class LoginFormTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.form_data = {
            "email": "testuser@example.com",
            "password": "password123",
        }

    def test_valid_form(self):
        form = LoginForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        self.form_data["email"] = "invalidemail"
        form = LoginForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class SetPasswordFormTests(TestCase):
    def setUp(self):
        self.form_data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }

    def test_valid_form(self):
        form = SetPasswordForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_password_too_short(self):
        self.form_data["new_password"] = "short"

        form = SetPasswordForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)

    def test_passwords_do_not_match(self):
        self.form_data["confirm_password"] = "mismatch"

        form = SetPasswordForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)
