from django.test import Client, TestCase
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated_index_response(self):
        """
        An unauthenticated user gets a valid response.
        """
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/index.html")

    def test_unauthenticated_about_response(self):
        """
        An unauthenticated user gets a valid response.
        """
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/about.html")
