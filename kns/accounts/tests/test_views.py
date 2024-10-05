from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from ..forms import ChangePasswordForm, LoginForm, SetPasswordForm
from ..utils import generate_verification_token

User = get_user_model()


class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
            is_active=True,
        )

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.user.is_active = True
        self.user.save()

        self.profile = self.user.profile
        self.profile.is_onboarded = True

        self.profile.save()

        self.token = generate_verification_token(self.user)

        self.profile.save_email_token(self.token)

        self.uidb64 = urlsafe_base64_encode(
            force_bytes(self.user.pk),
        )

        self.url = reverse(
            "accounts:verify_email",
            args=[
                self.uidb64,
                self.token,
            ],
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
        self.client.logout()

        self.user.profile.role = "leader"
        self.user.profile.save()

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
            reverse("core:index"),
        )

    def test_login_view_post_success(self):
        """
        Test that the login view handles successful login.
        """
        self.client.get(reverse("accounts:login"))

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": "testuser@example.com",
                "password": "oldpassword",
            },
        )

        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, reverse("core:index"))

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
            "Incorrect email or password. Please try again.",
            form.errors["__all__"],
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

    def test_login_view_post_permission_denied(self):
        """
        Test that the login view denies access to users who are not superusers
        and do not have the 'leader' role.
        """
        self.client.logout()  # Ensure the user is logged out

        # Create a user with a role other than 'leader'
        self.user.profile.role = "member"
        self.user.profile.save()

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "email": self.user.email,
                "password": "oldpassword",
            },
        )

        self.assertEqual(response.status_code, 200)

        form = response.context.get("login_form")

        self.assertIsInstance(form, LoginForm)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Access denied. You do not have the necessary permissions.",
            form.errors["__all__"],
        )

    def test_verify_email_success(self):
        """
        Test that the verify_email view successfully verifies the user's email
        if the token is valid.
        """
        response = self.client.get(self.url)

        # Refresh the user from the database to get the updated verified status
        self.user.refresh_from_db()

        self.assertTrue(self.user.verified)
        self.assertRedirects(
            response,
            reverse("core:index"),
        )

    def test_verify_email_failure(self):
        """
        Test that the verify_email view shows an error if the token is
        invalid.
        """
        # Generate an invalid token for the user
        uidb64 = urlsafe_base64_encode(
            force_bytes(self.user.pk),
        )
        invalid_token = "invalid-token"

        # Call the verify_email view with the incorrect token
        response = self.client.get(
            reverse(
                "accounts:verify_email",
                kwargs={"uidb64": uidb64, "token": invalid_token},
            )
        )

        # Refresh the user from the database to confirm their email is
        # not verified
        self.user.refresh_from_db()

        self.assertFalse(self.user.verified)
        self.assertTemplateUsed(
            response,
            "accounts/pages/verification_failed.html",
        )
        self.assertEqual(
            list(response.context["messages"])[0].message,
            "The verification link is invalid or has expired.",
        )

    def test_verification_email_view_success(self):
        """
        Test that the verification_email view sends a verification email
        successfully.
        """
        # Call the verification_email view for the user
        response = self.client.get(
            reverse(
                "accounts:verification_email",
                args=[self.user.pk],
            )
        )

        # Check if the user was redirected back to their dashboard or
        # profile page
        self.assertRedirects(
            response,
            reverse(
                "profiles:profile_overview",
                kwargs={
                    "profile_slug": self.user.profile.slug,
                },
            ),
        )

        # Check that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "Verify your email address",
            mail.outbox[0].subject,
        )

    def test_verification_email_view_permission_denied(self):
        """
        Test that the verification_email view denies access if the user
        is not the same or a superuser.
        """
        # Log out the current user
        self.client.logout()

        # Create another user and login
        User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
            verified=False,
        )

        self.client.login(
            email="otheruser@example.com",
            password="password123",
        )

        # Attempt to send a verification email for the original user
        response = self.client.get(
            reverse(
                "accounts:verification_email",
                args=[self.user.pk],
            )
        )

        self.assertEqual(response.status_code, 302)


class VerificationEmailTests(TestCase):
    def setUp(self):
        """
        Create a user for testing and set up any required data.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

    @patch("kns.accounts.views.send_verification_email")
    def test_verification_email_failure(
        self,
        mock_send_verification_email,
    ):
        """
        Test that the verification_email view handles exceptions from the
        send_verification_email function and displays an error message.
        """
        # Configure the mock to raise an exception
        mock_send_verification_email.side_effect = Exception(
            "Test exception",
        )

        # Call the verification_email view
        url = reverse(
            "accounts:verification_email",
            args=[
                self.user.pk,
            ],
        )
        response = self.client.get(url)

        # Check for error message in the response
        self.assertRedirects(
            response,
            reverse(
                "profiles:profile_overview",
                kwargs={
                    "profile_slug": self.user.profile.slug,
                },
            ),
        )


class AgreeToTermsViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
            is_active=True,
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.url = reverse(
            "accounts:agree_to_terms",
        )

    def test_agree_to_terms_view_redirect_when_already_agreed(self):
        """
        Test that an authenticated user who has already agreed to the
        terms is redirected to their profile page with appropriate message.
        """
        # Log in the user
        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        # Set agreed_to_terms to True
        self.user.agreed_to_terms = True
        self.user.save()

        response = self.client.get(self.url)

        # Check for redirection to profile page
        self.assertRedirects(
            response,
            self.user.profile.get_absolute_url(),
        )

        # Access messages from response
        messages = list(get_messages(response.wsgi_request))

        # Assert that one message exists
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You have already agreed to the Terms and Conditions.",
        )

    def test_agree_to_terms_view_post_success(self):
        """
        Test that an authenticated user can successfully agree to the
        terms and be redirected to their profile page.
        """
        response = self.client.post(
            self.url,
            data={
                "agree_checkbox": "on",
            },
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.agreed_to_terms)

        self.assertRedirects(
            response,
            self.user.profile.get_absolute_url(),
        )

        # Access messages from response
        messages = list(get_messages(response.wsgi_request))

        # Assert that one message exists
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You have successfully agreed to the Terms and Conditions.",
        )

    def test_agree_to_terms_view_post_failure(self):
        """
        Test that an authenticated user who does not check the checkbox
        receives an error message.
        """
        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "You must agree to the Terms and Conditions to proceed.",
        )

    def test_agree_to_terms_view_unauthenticated(self):
        """
        Test that an unauthenticated user is redirected to the login
        page when accessing the agree-to-terms view.
        """
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_agree_to_terms_view_post_success_unexpected_form(self):
        """
        Test that if the form is submitted with unexpected data, it
        still behaves as expected.
        """
        response = self.client.post(
            self.url,
            data={
                "unexpected_field": "value",
            },
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.agreed_to_terms)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "You must agree to the Terms and Conditions to proceed.",
        )


class SetPasswordViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
            is_active=True,
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

        self.member_user = User.objects.create_user(
            email="memberuser@example.com",
        )

        self.member_profile = self.member_user.profile

        self.member_profile.is_onboarded = True
        self.member_profile.role = "leader"
        self.member_profile.save()

        self.token = generate_verification_token(self.member_user)
        self.uidb64 = urlsafe_base64_encode(
            force_bytes(self.member_user.pk),
        )

        self.url = reverse(
            "accounts:set_password",
            args=[self.uidb64, self.token],
        )

    def test_set_password_success(self):
        """
        Test that the set_password view successfully sets
        a new password.
        """

        response = self.client.post(
            self.url,
            data={
                "new_password": "Newpassword@123",
                "confirm_password": "Newpassword@123",
            },
        )

        self.assertFalse(self.member_user.has_usable_password())

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

        self.member_user.refresh_from_db()
        self.assertTrue(self.member_user.check_password("Newpassword@123"))

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                "Your password has been set. "
                "Use your newly set password to login to KNT"
            ),
        )

    def test_set_password_invalid_token(self):
        """
        Test that the set_password view handles an invalid
        token correctly.
        """
        invalid_token = "invalid-token"
        url = reverse(
            "accounts:set_password",
            args=[self.uidb64, invalid_token],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/pages/set_password.html",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                "The link you are using has expired."
                "Please request a new link from your leader."
            ),
        )

    def test_set_password_already_set(self):
        """
        Test that the set_password view handles the case where the
        user already has a password set.
        """
        self.member_user.set_password("Newpassword@123")
        self.member_user.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                "You already have a password set. "
                "Please log in using your existing password."
            ),
        )

    def test_set_profile_role_is_not_leader(self):
        """
        Test that the set_password view handles the case where the
        user already has a password set.
        """
        self.member_user.set_password("Newpassword@123")
        self.member_user.save()

        self.member_profile.role = "member"
        self.member_profile.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You cannot complete this request",
        )

    def test_set_password_profile_not_found(self):
        """
        Test that the set_password view handles the case where the user
        profile is not found.
        """
        # Create an invalid UID to trigger a profile not found scenario
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(99999))
        url = reverse(
            "accounts:set_password",
            args=[invalid_uidb64, self.token],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(
            response,
            "404.html",
        )

    def test_set_password_post_form_invalid(self):
        """
        Test that the set_password view handles invalid form data.
        """
        response = self.client.post(
            self.url,
            data={
                "new_password": "short",
                "confirm_password": "short",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/pages/set_password.html",
        )

        form = response.context.get("set_password_form")

        self.assertFalse(form.is_valid())
        self.assertIsInstance(form, SetPasswordForm)

        self.assertIn(
            "Your password must be at least 8 characters",
            form.errors["new_password"],
        )
