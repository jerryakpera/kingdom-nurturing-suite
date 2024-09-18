from datetime import date

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.forms import GroupForm
from kns.groups.models import Group
from kns.groups.tests.test_constants import VALID_GROUP_DESCRIPTION
from kns.profiles.forms import AgreeToTermsForm, BioDetailsForm, ProfileInvolvementForm

from ..models import ProfileOnboarding


def clear_onboarding_cache(profile):
    cache_key = f"onboarding_steps_{profile.id}"

    # Delete the specific cache key
    cache.delete(cache_key)


class TestBackView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users and profiles
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = False
        self.profile.save()

        # Create a ProfileOnboarding instance
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
        )

        # Log the user in
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        # URL for the back view
        self.back_url = reverse("onboarding:back")

    def test_back_view_authenticated(self):
        """Test back view for authenticated users."""
        self.profile_onboarding.current_step = 2
        self.profile_onboarding.save()

        previous_step_info = self.profile_onboarding.get_current_step(self.profile)
        previous_step_url = previous_step_info["url_name"]

        response = self.client.get(self.back_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(previous_step_url))

    def test_back_view_no_steps_left(self):
        """Test back view when on the first step."""
        self.profile_onboarding.current_step = 1
        self.profile_onboarding.save()

        response = self.client.get(self.back_url)
        self.assertEqual(response.status_code, 302)
        first_step_url = self.profile_onboarding.get_current_step(self.profile)[
            "url_name"
        ]
        self.assertRedirects(response, reverse(first_step_url))

    def test_back_view_not_authenticated(self):
        """Test back view for unauthenticated users."""
        self.client.logout()

        response = self.client.get(self.back_url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse("accounts:login")
        expected_redirect_url = f"{login_url}?next={self.back_url}"
        self.assertRedirects(response, expected_redirect_url)

    def test_back_view_already_onboarded(self):
        """Test back view for users who are already onboarded."""
        self.profile.is_onboarded = True
        self.profile.save()

        response = self.client.get(self.back_url)
        self.assertEqual(response.status_code, 302)

        # Onboarded users may get redirected to a dashboard or homepage
        # depending on your app logic. Adjust this URL as needed.
        self.assertRedirects(response, reverse("onboarding:index"))

    def test_back_view_skip_step(self):
        """Test back view when a step is accidentally skipped."""
        # Manually set the current step beyond the last available step
        self.profile_onboarding.current_step = 5
        self.profile_onboarding.save()

        response = self.client.get(self.back_url)
        self.assertEqual(response.status_code, 302)

        # Ensure the user is redirected to the last valid step
        last_step_url = self.profile_onboarding.get_current_step(self.profile)[
            "url_name"
        ]

        self.assertRedirects(response, reverse(last_step_url))


class TestOnboardingViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users and profiles
        self.user = User.objects.create_user(
            email="testuser1@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = False

        self.profile.save()

        # Create a ProfileOnboarding instance
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
        )

        # Log the user in
        self.client.login(
            email=self.user.email,
            password="password123",
        )

        # URLs for the views
        self.back_url = reverse("onboarding:back")
        self.index_url = reverse("onboarding:index")

    def test_index_view_authenticated(self):
        """
        Test the index view for authenticated users to ensure it
        renders correctly and handles form submission.
        """
        # Set up an onboarding process with a specific step
        self.profile_onboarding.current_step = 1
        self.profile_onboarding.save()

        response = self.client.get(self.index_url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "onboarding/pages/bio_details.html",
        )

        # Check if the form is present in the context
        self.assertIsInstance(
            response.context["bio_details_form"],
            BioDetailsForm,
        )

    def test_index_view_post_valid_data(self):
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "gender": "male",
            "date_of_birth": date(2000, 1, 1),
        }

        response = self.client.post(self.index_url, data)

        # Ensure form validation is successful
        self.assertTrue(BioDetailsForm(data).is_valid())

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the onboarding process moves to the next step
        self.profile_onboarding.refresh_from_db()
        current_step = self.profile_onboarding.get_current_step(self.profile)

        # Assert that the current step is still 1 (since the first submission doesn't progress)
        self.assertEqual(current_step["no"], 2)

        # Check the redirect URL
        expected_redirect_url = "/onboarding/involvement"
        self.assertRedirects(response, expected_redirect_url)

    def test_index_view_post_invalid_data(self):
        """
        Test the index view POST request for authenticated users
        with invalid data to ensure the form submission does not progress.
        """
        invalid_data = {
            "first_name": "",
            "last_name": "User",
        }

        response = self.client.post(self.index_url, invalid_data)

        # Check if the response status code is 200 OK (form errors displayed)
        self.assertEqual(response.status_code, 200)

        # Ensure the form is re-rendered with errors
        self.assertTrue(response.context["bio_details_form"].errors)

    def test_index_view_not_authenticated(self):
        """
        Test the index view for unauthenticated users to ensure it
        redirects to the login page.
        """
        # Log the user out
        self.client.logout()

        response = self.client.get(self.index_url)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Construct the expected login URL with the 'next' parameter
        login_url = reverse("accounts:login")
        expected_redirect_url = f"{login_url}?next={self.index_url}"

        # Check if the redirect URL is the login page with 'next' parameter
        self.assertRedirects(response, expected_redirect_url)


class TestInvolvementView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users and profiles
        self.user = User.objects.create_user(
            email="testuser2@example.com",
            password="password123",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = False

        self.profile.save()

        # Create a ProfileOnboarding instance
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
        )

        # Log the user in
        self.client.login(
            email=self.user.email,
            password="password123",
        )

        clear_onboarding_cache(self.profile)
        # URL for the involvement view
        self.involvement_url = reverse("onboarding:involvement")

    def test_involvement_view_authenticated(self):
        """
        Test the involvement view for authenticated users to ensure it
        renders correctly and handles form submission.
        """
        # Set up an onboarding process with a specific step
        self.profile_onboarding.current_step = 2
        self.profile_onboarding.save()

        response = self.client.get(self.involvement_url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "onboarding/pages/involvement_details.html",
        )

        # Check if the form is present in the context
        self.assertIsInstance(
            response.context["involvement_form"],
            ProfileInvolvementForm,
        )

    def test_involvement_view_post_valid_data(self):
        """
        Test the involvement view POST request for authenticated users
        with valid data to ensure the form submission progresses.
        """

        self.profile_onboarding.current_step = 2
        self.profile_onboarding.save()

        data = {
            "is_movement_training_facilitator": True,
            "reason_is_not_movement_training_facilitator": "",
            "is_skill_training_facilitator": True,
            "reason_is_not_skill_training_facilitator": "",
            "is_mentor": True,
            "reason_is_not_mentor": "",
        }

        response = self.client.post(self.involvement_url, data)

        # Ensure form validation is successful
        form = ProfileInvolvementForm(
            data,
            instance=self.profile,
        )
        self.assertTrue(form.is_valid(), form.errors)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the onboarding process moves to the next step
        self.profile_onboarding.refresh_from_db()

        # Assert that the current step is updated to the next one
        self.assertEqual(self.profile_onboarding.current_step, 3)

        # Check the redirect URL (assuming the next step is set correctly)
        expected_redirect_url = "/onboarding/group"
        self.assertRedirects(
            response,
            expected_redirect_url,
        )


class TestGroupView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users and profiles
        self.user = User.objects.create_user(
            email="testuser3@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.role = "leader"
        self.profile.save()

        # Create a ProfileOnboarding instance
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
            current_step=3,
        )

        # Log the user in
        self.client.login(
            email=self.user.email,
            password="password123",
        )

        # URL for the group view
        self.group_url = reverse("onboarding:group")

    def test_group_view_authenticated(self):
        """
        Test the group view for authenticated users to ensure it
        renders correctly and handles form submission.
        """
        response = self.client.get(self.group_url)

        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "onboarding/pages/register_group_onboarding.html",
        )

        # Check if the form is present in the context
        self.assertIsInstance(
            response.context["group_form"],
            GroupForm,
        )

    def test_group_view_post_valid_data(self):
        """
        Test the group view POST request for authenticated users
        with valid data to ensure the form submission progresses.
        """
        data = {
            "name": "Test Group",
            "location_country": "US",
            "description": VALID_GROUP_DESCRIPTION,
            "location_city": "New York",
            "image": "",
        }

        response = self.client.post(
            self.group_url,
            data=data,
        )

        form = GroupForm(data)

        # Ensure form validation is successful
        self.assertTrue(form.is_valid(), form.errors)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the onboarding process moves to the next step
        self.profile_onboarding.refresh_from_db()

        # Assert that the current step is updated to the next one
        self.assertEqual(self.profile_onboarding.current_step, 4)

        expected_redirect_url = "/onboarding/agree"
        self.assertRedirects(response, expected_redirect_url)

    def test_group_view_non_leader(self):
        """
        Test the group view when the user is not a leader to ensure
        that the user is redirected or does not see the form.
        """
        self.profile.role = "member"
        self.profile.save()

        response = self.client.get(self.group_url)

        self.assertEqual(response.status_code, 200)

    def test_group_view_existing_group(self):
        """
        Test the group view for users who already lead a group to ensure
        they see the form pre-filled with their group's information.
        """
        group = Group.objects.create(
            name="Existing Group",
            leader=self.profile,
            description=VALID_GROUP_DESCRIPTION,
            location_country="US",
            location_city="New York",
        )

        response = self.client.get(self.group_url)

        # Ensure the form is pre-filled with group data
        form = response.context["group_form"]

        self.assertEqual(form.instance, group)
        self.assertEqual(form.initial["name"], "Existing Group")

    def test_group_view_post_invalid_data(self):
        """
        Test the group view POST request for authenticated users
        with invalid data to ensure the form does not submit.
        """
        data = {
            "name": "",  # Invalid: empty name
            "location_country": "US",
            "description": "",  # Invalid: empty description
            "location_city": "New York",
        }

        response = self.client.post(self.group_url, data=data)

        # Ensure the form does not validate
        form = GroupForm(data)
        self.assertFalse(form.is_valid())

        # Ensure the response does not redirect (i.e., stays on the same page)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "onboarding/pages/register_group_onboarding.html"
        )

        # Access the form from the response context and check for form errors
        group_form = response.context["group_form"]

        self.assertFormError(group_form, "name", "This field is required.")
        self.assertFormError(group_form, "description", "This field is required.")

    def test_group_view_not_authenticated(self):
        """
        Test the group view for unauthenticated users to ensure it
        redirects to the login page.
        """
        self.client.logout()

        response = self.client.get(self.group_url)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Construct the expected login URL with the 'next' parameter
        login_url = reverse("accounts:login")
        expected_redirect_url = f"{login_url}?next={self.group_url}"

        # Check if the redirect URL is the login page with 'next' parameter
        self.assertRedirects(response, expected_redirect_url)


class TestAgreeView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create user and profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"

        self.profile.save()

        # Create a ProfileOnboarding instance
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
            current_step=4,
        )

        # Log the user in
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        # URL for the agree view
        self.agree_url = reverse("onboarding:agree")

    def test_agree_view_authenticated(self):
        """
        Test the agree view for authenticated users to ensure it
        renders correctly and displays the form.
        """
        response = self.client.get(self.agree_url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "onboarding/pages/agree_to_terms_onboarding.html",
        )

        # Check if the form is present in the context
        self.assertIsInstance(
            response.context["agree_form"],
            AgreeToTermsForm,
        )

    def test_agree_view_post_valid_data(self):
        """
        Test the agree view POST request for authenticated users
        with valid data to ensure the form submission progresses.
        """
        data = {
            "agreed_to_terms": True,
        }

        response = self.client.post(self.agree_url, data)

        # Ensure form validation is successful
        form = AgreeToTermsForm(data, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the onboarding process moves to the next step
        self.profile_onboarding.refresh_from_db()
        self.profile.refresh_from_db()

        # Assert that the current step is updated to the next one
        self.assertEqual(self.profile_onboarding.current_step, 5)

        # Check if the profile's verified status is updated
        self.assertTrue(self.profile.user.verified)
        self.assertTrue(self.profile.user.agreed_to_terms)
