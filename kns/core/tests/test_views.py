from django.test import Client, TestCase
from django.urls import reverse

from ..models import FAQ


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up some FAQ data for testing
        FAQ.objects.create(
            question="What is the Kingdom Nurturing Suite (KNS)?",
            answer="A comprehensive collection of tools for DMM.",
        )

        FAQ.objects.create(
            question="How can I register a new DBS group in KNS?",
            answer="Register a new DBS group through the KNS web app.",
        )

    def test_index_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/index.html")

    def test_about_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/about.html")

    def test_faqs_response(self):
        """
        An user gets a valid response and sees the FAQ content.
        """
        response = self.client.get(reverse("core:faqs"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/faqs.html")

        # Check if the FAQs are being passed to the context
        self.assertIn("faqs", response.context)

    def test_submit_ticket_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:submit_ticket"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "core/pages/submit_ticket.html",
        )
