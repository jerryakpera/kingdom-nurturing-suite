from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from kns.custom_user.models import User
from kns.levels.models import Level, Sublevel


class LevelViewsTestCase(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests. Creates sample Level and Sublevel objects.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        # Create sample Level objects
        self.level1 = Level.objects.create(
            title="Level 1",
            content="Content for level 1",
            author=self.profile,
        )
        self.level2 = Level.objects.create(
            title="Level 2",
            content="Content for level 2",
            author=self.profile,
        )

        # Create sample Sublevel objects
        self.sublevel1 = Sublevel.objects.create(
            title="Sublevel 1",
            content="Content for sublevel 1",
            author=self.profile,
        )
        self.sublevel2 = Sublevel.objects.create(
            title="Sublevel 2",
            content="Content for sublevel 2",
            author=self.profile,
        )

        # Initialize API client for making HTTP requests
        self.client = APIClient()

    def test_levels_list(self):
        """
        Test the levels_list view to ensure it returns a list of all levels.
        """
        url = reverse("api:levels_list")
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct number of levels
        data = response.json()
        self.assertEqual(len(data["levels"]), 2)

        # Check if the response contains the correct level titles
        level_titles = [level["title"] for level in data["levels"]]

        self.assertIn("Level 1", level_titles)
        self.assertIn("Level 2", level_titles)

        def test_level_detail(self):
            """
            Test the level_detail view to ensure it returns the correct
            details for a specific level.
            """
            url = reverse("api:level_detail", args=[self.level1.id])
            response = self.client.get(url)

            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

            # Check if the response is JSON
            self.assertIsInstance(response, JsonResponse)

            # Check if the response contains the correct level details
            data = response.json()
            self.assertEqual(
                data["level"]["title"],
                "Level 1",
            )
            self.assertEqual(
                data["level"]["content"],
                "Content for level 1",
            )

    def test_level_detail(self):
        """
        Test the level_detail view to ensure it returns the correct
        details for a specific level.
        """
        url = reverse("api:level_detail", args=[self.level1.id])
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct level details
        data = response.json()
        self.assertEqual(data["level"]["title"], "Level 1")
        self.assertEqual(
            data["level"]["content"],
            "Content for level 1",
        )

    def test_sublevels_list(self):
        """
        Test the sublevels_list view to ensure it returns a list of all sublevels.
        """
        url = reverse("api:sublevels_list")
        response = self.client.get(url)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response is JSON
        self.assertIsInstance(response, JsonResponse)

        # Check if the response contains the correct number of sublevels
        data = response.json()
        self.assertEqual(len(data["sublevels"]), 2)

        # Check if the response contains the correct sublevel titles
        sublevel_titles = [sublevel["title"] for sublevel in data["sublevels"]]
        self.assertIn("Sublevel 1", sublevel_titles)
        self.assertIn("Sublevel 2", sublevel_titles)
