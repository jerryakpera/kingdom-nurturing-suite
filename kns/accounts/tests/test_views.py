from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import ChangePasswordForm, LoginForm

User = get_user_model()


class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

    def test_index_view(self):
        """
        Test that the user dashboard (index) view is accessible and
        context contains the expected data.
        """
        response = self.client.get(reverse("accounts:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "accounts/pages/index.html",
        )

        # Check if the context contains the correct data
        self.assertIn("user", response.context)
        self.assertEqual(response.context["user"], self.user)

    def test_login_view_get_authenticated(self):
        """
        Test that authenticated users are redirected away
        from the login view.
        """
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:index"))

    def test_login_view_post_failure_authenticated(self):
        """
        Test that authenticated users are redirected away from the
        login view even if they attempt a login request.
        """
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": "testuser@example.com",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:index"))

    def test_login_view_get_unauthenticated(self):
        """
        Test that the login view renders the login form for
        unauthenticated users.
        """
        self.client.logout()  # Ensure the user is not authenticated
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/pages/login.html",
        )
        self.assertIsInstance(
            response.context["login_form"],
            LoginForm,
        )

    def test_login_view_post_success_unauthenticated(self):
        """
        Test that the login view handles successful login for unauthenticated users.
        """
        self.client.logout()  # Ensure the user is not authenticated
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": "testuser@example.com",
                "password": "oldpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("accounts:index"),
        )

    def test_login_view_post_success(self):
        """
        Test that the login view handles successful login.
        """
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": "testuser@example.com",
                "password": "oldpassword",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:index"))

    def test_login_view_post_failure(self):
        """
        Test that the login view handles failed login.
        """

        self.client.logout()

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": "testuser@example.com",
                "password": "wrongpassword",
            },
        )

        self.assertEqual(response.status_code, 200)

        form = response.context.get("login_form")

        self.assertIsInstance(form, LoginForm)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Incorrect email or password. Please try again.", form.errors["__all__"]
        )

    def test_logout_view(self):
        """
        Test that the logout view logs out the user and redirects to login.
        """
        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_change_password_view_get(self):
        """
        Test that the change password view renders the form correctly.
        """
        response = self.client.get(reverse("accounts:change_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/pages/change_password.html")
        self.assertIsInstance(
            response.context["change_password_form"], ChangePasswordForm
        )

    def test_change_password_view_post_success(self):
        """
        Test that the change password view handles successful password change.
        """
        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "current_password": "oldpassword",
                "new_password": "newpassword123",
                "confirm_new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:index"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))
        self.assertEqual(len(mail.outbox), 1)

    def test_change_password_view_post_incorrect_current_password(self):
        """
        Test that the change password view provides an
        error for incorrect current password.
        """
        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "current_password": "incorrectpassword",
                "new_password": "newpassword123",
                "confirm_new_password": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)

        form = response.context.get("change_password_form")

        self.assertIsInstance(form, ChangePasswordForm)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "You entered an incorrect password",
            form.errors["current_password"],
        )
