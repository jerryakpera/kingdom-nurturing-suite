from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.profiles.forms import ConsentFormSubmission
from kns.profiles.models import ConsentForm, Profile


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        User.objects.create_user(
            email="adminuser@example.com",
            password="oldpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_index_view(self):
        """
        Test the index view to ensure it renders correctly and lists profiles.
        """
        response = self.client.get(reverse("profiles:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/index.html")

        self.assertIn("profiles", response.context)
        self.assertEqual(
            response.context["profiles"].count(),
            1,
        )

        # Ensure the profile is listed
        assert b"Test User" in response.content

    def test_profile_detail_view(self):
        """
        Test the profile_detail view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/profile_detail.html")

        # Ensure the profile details are present
        self.assertIn("Test User", response.content.decode())

    def test_profile_detail_view_not_found(self):
        """
        Test the profile_detail view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_profile_involvements_view(self):
        """
        Test the profile_involvements view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_involvements.html",
        )

        # Ensure the profile involvementss are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_involvements_view_not_found(self):
        """
        Test the profile_involvements view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_trainings_view(self):
        """
        Test the profile_trainings view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_trainings.html",
        )

        # Ensure the profile trainingss are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_trainings_view_not_found(self):
        """
        Test the profile_trainings view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_activities_view(self):
        """
        Test the profile_activities view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_activities.html",
        )

        # Ensure the profile activitiess are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_activities_view_not_found(self):
        """
        Test the profile_activities view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_settings_view(self):
        """
        Test the profile_settings view to ensure it renders and
        updates the profile settings.
        """

        # Get the profile settings page
        response = self.client.get(self.profile.get_settings_url())

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_settings.html",
        )

        # Ensure the form is present in the response
        self.assertIn("profile_settings_form", response.context)

        # Now test the POST request to update the profile settings
        new_data = {
            "bio_details_is_visible": False,
            "contact_details_is_visible": False,
            # Add other profile fields here if necessary
        }

        response = self.client.post(
            self.profile.get_settings_url(),
            data=new_data,
        )

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.bio_details_is_visible,
            False,
        )
        self.assertEqual(
            self.profile.contact_details_is_visible,
            False,
        )

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)

        # Ensure the success message is in the messages
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.profile.get_full_name()} settings updated",
        )


class ConsentFormViewTests(TestCase):
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

        # Create a profile for the user
        self.profile = self.user.profile

        self.valid_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf",
        )

        self.invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file_content",
            content_type="text/plain",
        )

    def test_upload_consent_form_page(self):
        """
        Test accessing the upload consent form page.
        """
        url = reverse(
            "profiles:upload_consent_form",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/submit_consent_form.html",
        )

        # Ensure the form is present in the response
        self.assertIn("form", response.context)
        self.assertIsInstance(
            response.context["form"],
            ConsentFormSubmission,
        )

    @patch("cloudinary.uploader.upload_image")
    def test_successful_consent_form_upload(self, mock_upload_image):
        # Adjust the mock return value
        mock_upload_image.return_value = "http://example.com/test_image.jpg"

        url = reverse(
            "profiles:upload_consent_form",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        response = self.client.post(
            url,
            {
                "consent_form": self.valid_file,
            },
        )

        # Check if the response redirects after saving
        self.assertEqual(
            response.status_code,
            200,
        )

        # Ensure the success message is in the messages
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "There was an error uploading the consent form.",
        )

    def test_invalid_consent_form_upload(self):
        """
        Test uploading an invalid consent form.
        """
        url = reverse(
            "profiles:upload_consent_form", kwargs={"profile_slug": self.profile.slug}
        )

        response = self.client.post(url, {"consent_form": self.invalid_file})

        # Check if the response status code is 200 OK (since the form is not valid)
        self.assertEqual(response.status_code, 200)

        # Ensure the error message is in the messages
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "The consent form must be a PDF, JPG, or PNG file."
        )

    # def test_existing_consent_form_replacement(self):
    #     """
    #     Test that uploading a new consent form replaces an existing one.
    #     """
    #     # Create an existing consent form
    #     ConsentForm.objects.create(
    #         profile=self.profile,
    #         consent_form=self.valid_file,
    #         submitted_by=self.user.profile,
    #     )

    #     url = reverse(
    #         "profiles:upload_consent_form", kwargs={"profile_slug": self.profile.slug}
    #     )
    #     new_file = SimpleUploadedFile(
    #         "new_test.pdf", b"new_file_content", content_type="application/pdf"
    #     )

    #     response = self.client.post(url, {"consent_form": new_file})

    #     # Check if the response redirects after saving
    #     self.assertEqual(response.status_code, 302)

    #     # Verify the existing consent form was replaced
    #     consent_form = ConsentForm.objects.get(profile=self.profile)
    #     self.assertEqual(consent_form.consent_form.name, "new_test.pdf")


# def test_upload_consent_form_unauthorized(self):
#     """
#     Test accessing the upload consent form page with an unauthenticated user.
#     """
#     self.client.logout()

#     url = reverse(
#         "profiles:upload_consent_form", kwargs={"profile_slug": self.profile.slug}
#     )
#     response = self.client.get(url)

#     # Check if the response redirects to the login page
#     self.assertEqual(response.status_code, 302)
#     self.assertRedirects(response, f"/accounts/login/?next={url}")

#     # Ensure the user is redirected to the login page
