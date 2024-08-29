from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.utils import timezone

from kns.profiles.utils import calculate_max_dob, get_profile_slug, name_with_apostrophe


class TestGetProfileSlug(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_valid_slug(self, mock_resolve):
        """
        Test if a valid profile slug is extracted correctly from the URL path.
        """
        # Mock the resolve function to return a match with profile_slug
        mock_resolve.return_value.kwargs = {"profile_slug": "test-slug"}

        request = self.factory.get("/profiles/test-slug/")
        request.path_info = "/profiles/test-slug/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "test-slug")

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_non_profiles_path(self, mock_resolve):
        """
        Test if no slug is extracted when the path does not start with /profiles/.
        """
        # Mock the resolve function, though it shouldn't be called in this case
        mock_resolve.return_value.kwargs = {}

        request = self.factory.get("/some/other/path/")
        request.path_info = "/some/other/path/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "")

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_no_slug(self, mock_resolve):
        """
        Test if no slug is extracted when the path is correct but no slug is present.
        """
        # Mock the resolve function to return an empty kwargs
        mock_resolve.return_value.kwargs = {}

        request = self.factory.get("/profiles/")
        request.path_info = "/profiles/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "")


class TestCalculateMaxDob(TestCase):
    def test_calculate_max_dob(self):
        """
        Test that calculate_max_dob returns the correct date for a given age.
        """
        # Assume today's date is 2024-08-29
        age = 30
        expected_max_dob = (
            timezone.now().date() - timedelta(days=(age * 365))
        ).strftime("%Y-%m-%d")
        self.assertEqual(calculate_max_dob(age), expected_max_dob)


class TestNameWithApostrophe(TestCase):
    def test_name_with_apostrophe_ends_with_s(self):
        """
        Test that name_with_apostrophe adds just an apostrophe if the name ends with 's'.
        """
        name = "James"
        result = name_with_apostrophe(name)
        self.assertEqual(result, "James'")

    def test_name_with_apostrophe_does_not_end_with_s(self):
        """
        Test that name_with_apostrophe adds 's if the name does not end with 's'.
        """
        name = "John"
        result = name_with_apostrophe(name)
        self.assertEqual(result, "John's")
