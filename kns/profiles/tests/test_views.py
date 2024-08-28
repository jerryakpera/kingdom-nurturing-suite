from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User


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

    def test_edit_bio_details_get(self):
        """
        Test the edit_bio_details view renders the form correctly.
        """
        url = reverse(
            "profiles:edit_bio_details",
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
            "profiles/pages/edit_bio_details.html",
        )

        # Ensure the form is present in the context
        self.assertIn(
            "bio_details_form",
            response.context,
        )

    def test_edit_bio_details_view_not_found(self):
        """
        Test the edit_bio_details view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:edit_bio_details",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_edit_bio_details_post_valid(self):
        """
        Test posting valid data to edit_bio_details view updates the profile.
        """
        url = reverse(
            "profiles:edit_bio_details",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "gender": "male",
            "date_of_birth": "2000-01-01",
            "place_of_birth_country": "NG",
            "place_of_birth_city": "City",
        }
        response = self.client.post(
            url,
            data=data,
        )

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        # Check if the profile was updated
        self.assertEqual(self.profile.first_name, "Updated")
        self.assertEqual(self.profile.last_name, "User")
        self.assertEqual(self.profile.gender, "male")
        self.assertEqual(str(self.profile.date_of_birth), "2000-01-01")
        self.assertEqual(self.profile.place_of_birth_country, "NG")
        self.assertEqual(self.profile.place_of_birth_city, "City")

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            self.profile.get_absolute_url(),
        )

        # Ensure the success message is in the messages
        messages = list(
            response.wsgi_request._messages,
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Profile updated",
        )

    def test_edit_bio_details_post_invalid(self):
        """
        Test posting invalid data to edit_bio_details view does not update the profile.
        """
        url = reverse(
            "profiles:edit_bio_details",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "first_name": "",  # Invalid as it is required
            "last_name": "User",
        }
        response = self.client.post(url, data=data)

        # The profile should not be updated
        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.first_name, "")
        self.assertEqual(self.profile.first_name, "Test")

        # Check if the response does not redirect
        self.assertEqual(response.status_code, 200)

        # Extract the form from the response context
        form = response.context.get("bio_details_form")

        # Ensure the form contains errors
        self.assertIsNotNone(
            form,
            "Form is not present in the response context",
        )
        self.assertTrue(
            form.errors,
            "Form should contain errors",
        )

        self.assertIn(
            "first_name",
            form.errors,
            "First name field should have errors",
        )
        self.assertIn(
            "This field is required.",
            form.errors["first_name"],
            "Expected error message not found",
        )

    def test_edit_contact_details_get(self):
        """
        Test the edit_contact_details view renders the form correctly.
        """
        url = reverse(
            "profiles:edit_contact_details",
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
            "profiles/pages/edit_contact_details.html",
        )

        # Ensure the form is present in the context
        self.assertIn(
            "contact_details_form",
            response.context,
        )

    def test_edit_contact_details_view_not_found(self):
        """
        Test the edit_contact_details view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:edit_contact_details",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_edit_contact_details_post_valid(self):
        """
        Test posting valid data to edit_contact_details view updates the profile.
        """
        url = reverse(
            "profiles:edit_contact_details",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "phone_prefix": "+1",
            "phone": "1234567890",
            "email": "newemail@example.com",
            "location_city": "New City",
            "location_country": "US",
        }
        response = self.client.post(
            url,
            data=data,
        )

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        # Check if the profile was updated
        self.assertEqual(
            self.profile.email,
            "newemail@example.com",
        )
        self.assertEqual(
            self.profile.phone_prefix,
            "+1",
        )
        self.assertEqual(
            self.profile.phone,
            "1234567890",
        )
        self.assertEqual(
            self.profile.location_city,
            "New City",
        )
        self.assertEqual(
            self.profile.location_country,
            "US",
        )

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            self.profile.get_absolute_url(),
        )

        # Ensure the success message is in the messages
        messages = list(
            response.wsgi_request._messages,
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Profile contact details updated.",
        )

    def test_edit_contact_details_post_invalid(self):
        """
        Test posting invalid data to edit_contact_details view does not update the profile.
        """
        url = reverse(
            "profiles:edit_contact_details",
            kwargs={"profile_slug": self.profile.slug},
        )
        data = {
            "phone_prefix": "",
            "phone": "",
            "email": "invalid-email",
            "location_city": "",
            "location_country": "",
        }
        response = self.client.post(url, data=data)

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        # Check if the profile details remain unchanged
        self.assertEqual(self.profile.email, "testuser@example.com")
        self.assertEqual(self.profile.phone_prefix or "", "")
        self.assertEqual(self.profile.phone or "", "")
        self.assertEqual(self.profile.location_city or "", "")
        self.assertEqual(self.profile.location_country or "", "")

        # Check if the response does not redirect
        self.assertEqual(response.status_code, 200)

        # Extract the form from the response context
        form = response.context.get("contact_details_form")

        # Ensure the form contains errors
        self.assertIsNotNone(form, "Form is not present in the response context")
        self.assertTrue(form.errors, "Form should contain errors")

        # Check specific errors
        self.assertIn(
            "phone_prefix", form.errors, "Phone prefix field should have errors"
        )
        self.assertIn(
            "This field is required.",
            form.errors["phone_prefix"],
            "Expected error message not found for phone_prefix",
        )

        self.assertIn("email", form.errors, "Email field should have errors")
        self.assertIn(
            "Enter a valid email address.",
            form.errors["email"],
            "Expected error message not found for email",
        )
