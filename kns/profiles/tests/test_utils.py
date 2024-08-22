from unittest.mock import patch

from django.test import RequestFactory, TestCase

from kns.profiles.utils import get_profile_slug


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
