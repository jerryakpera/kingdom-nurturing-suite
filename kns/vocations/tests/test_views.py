from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.profiles.models import Profile
from kns.vocations.models import Vocation


class VocationViewsTest(TestCase):
    def setUp(self):
        # Set up test data
        self.client = Client()

        # Create a user and a profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"

        self.profile.save()

        # Create a vocation
        self.vocation = Vocation.objects.create(
            title="Software Developer",
            description="Builds and maintains software systems.",
            author=self.profile,
        )

    def test_index_view(self):
        """
        Test the index view returns a 200 status and uses the correct template.
        """
        response = self.client.get(reverse("vocations:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vocations/pages/index.html")

    def test_vocation_detail_view_not_found(self):
        """
        Test the vocation_detail view with an invalid vocation ID (404 response).
        """
        invalid_id = self.vocation.id + 1  # Generate an invalid ID
        url = reverse(
            "vocations:vocation_detail",
            kwargs={
                "vocation_id": invalid_id,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_vocation_detail_view(self):
        """
        Test the vocation_detail view with a valid vocation ID.
        """
        url = reverse(
            "vocations:vocation_detail",
            kwargs={
                "vocation_id": self.vocation.id,
            },
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "vocations/pages/vocation_detail.html",
        )

        self.assertContains(response, self.vocation.title)
