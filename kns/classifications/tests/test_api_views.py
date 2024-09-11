from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from kns.classifications.models import Classification, Subclassification
from kns.custom_user.models import User


class ClassificationViewsTestCase(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests. Creates sample Classification
        and Subclassification objects.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        # Create sample Classification objects
        self.classification1 = Classification.objects.create(
            title="Classification 1",
            content="Content for classification 1",
            author=self.profile,
            order=1,  # Add a valid value for the order field
        )
        self.classification2 = Classification.objects.create(
            title="Classification 2",
            content="Content for classification 2",
            author=self.profile,
            order=2,  # Add a valid value for the order field
        )

        # Create sample Subclassification objects
        self.subclassification1 = Subclassification.objects.create(
            title="Subclassification 1",
            content="Content for subclassification 1",
            author=self.profile,
        )
        self.subclassification2 = Subclassification.objects.create(
            title="Subclassification 2",
            content="Content for subclassification 2",
            author=self.profile,
        )

        # Initialize API client for making HTTP requests
        self.client = APIClient()

    def test_classifications_list(self):
        """
        Test the classifications_list view to ensure it returns a list
        of all classifications.
        """
        url = reverse("api:classifications_list")
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct number of classifications
        data = response.json()
        self.assertEqual(len(data["classifications"]), 2)

        # Check if the response contains the correct classification titles
        classification_titles = [
            classification["title"] for classification in data["classifications"]
        ]

        self.assertIn("Classification 1", classification_titles)
        self.assertIn("Classification 2", classification_titles)

    def test_classification_detail(self):
        """
        Test the classification_detail view to ensure it returns the correct
        details for a specific classification.
        """
        url = reverse(
            "api:classification_detail",
            args=[self.classification1.id],
        )
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct classification details
        data = response.json()
        self.assertEqual(data["classification"]["title"], "Classification 1")
        self.assertEqual(
            data["classification"]["content"], "Content for classification 1"
        )

    def test_subclassifications_list(self):
        """
        Test the subclassifications_list view to ensure it returns a list
        of all subclassifications.
        """
        url = reverse("api:subclassifications_list")
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct number of subclassifications
        data = response.json()
        self.assertEqual(len(data["subclassifications"]), 2)

        # Check if the response contains the correct subclassification titles
        subclassification_titles = [
            subclassification["title"]
            for subclassification in data["subclassifications"]
        ]

        self.assertIn("Subclassification 1", subclassification_titles)
        self.assertIn("Subclassification 2", subclassification_titles)
