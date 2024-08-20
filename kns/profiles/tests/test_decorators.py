from django.contrib import messages
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User

from ..decorators import profile_required
from ..models import Profile


class TestProfileRequiredDecorator(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user with a profile
        self.user_with_profile = User.objects.create_user(
            email="user_with_profile@example.com",
            password="testpass",
        )

        # Create a user without a profile
        self.user_without_profile = User.objects.create_user(
            email="user_without_profile@example.com",
            password="testpass",
        )

        self.user_without_profile.profile.delete()

        # URL for testing the view with the profile_required decorator
        self.test_url = reverse("groups:register_group")

    def test_redirect_if_no_profile(self):
        """
        A user without a profile is redirected to the profile setup.
        """
        self.client.login(
            email="user_without_profile@example.com",
            password="testpass",
        )

        response = self.client.get(self.test_url, follow=True)

        # Check the final response code and redirection
        self.assertRedirects(
            response,
            "/groups/",
            status_code=302,
            target_status_code=200,
        )

        messages_list = list(
            messages.get_messages(
                response.wsgi_request,
            )
        )

        self.assertTrue(messages_list)
        self.assertEqual(
            messages_list[0].message,
            "You need a profile to access that page.",
        )

    def test_access_if_has_profile(self):
        """
        A user with a profile can access the protected view.
        """
        self.client.login(
            email="user_with_profile@example.com",
            password="testpass",
        )

        response = self.client.get(self.test_url)

        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_authenticated(self):
        """
        An unauthenticated user is redirected to the login page.
        """
        response = self.client.get(self.test_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.test_url}",
        )
