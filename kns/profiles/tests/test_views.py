from datetime import date

from django.contrib.messages import get_messages
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.faith_milestones.models import FaithMilestone, ProfileFaithMilestone
from kns.groups.models import Group
from kns.groups.tests import test_constants
from kns.profiles.models import EncryptionReason, ProfileEncryption
from kns.skills.models import ProfileInterest, ProfileSkill, Skill


class TestViews(TestCase):
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

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        # Create another profile that should be excluded by the filtering logic
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password",
        )

        self.profile2 = self.user2.profile

        # Create group and descendant groups
        # Create a group
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.child_group = Group.objects.create(
            leader=self.profile2,
            name="Test Group 2",
            slug="test-group-2",
            description=test_constants.VALID_GROUP_DESCRIPTION,
            parent=self.group,
        )

        self.user3 = User.objects.create_user(
            email="childuser@example.com",
            password="password",
        )

        self.profile3 = self.user3.profile

        self.profile3.first_name = "Test3"
        self.profile3.last_name = "User"

        self.profile3.save()

        self.settings = Setting.get_or_create_setting()

        # Create faith milestones to use in the tests
        self.faith_milestone_1 = FaithMilestone.objects.create(
            title="Baptized",
            description="Sample description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone_2 = FaithMilestone.objects.create(
            title="Completed Discipleship Course",
            description="Sample description for a faith milestone",
            author=self.profile,
        )

    def test_index_view(self):
        """
        Test the index view to ensure it renders correctly and lists profiles.
        """
        response = self.client.get(reverse("profiles:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/index.html")

        # Check if 'page_obj' is in context and is a Page instance
        self.assertIn("page_obj", response.context)
        self.assertIsInstance(response.context["page_obj"], Page)

        # Check that the excluded profile is not in the page object
        self.assertNotIn(
            self.profile2,
            response.context["page_obj"].object_list,
        )

        # Check that the child profile is included in the page object
        self.assertIn(
            self.profile3,
            response.context["page_obj"].object_list,
        )

        # Ensure the profiles are listed
        self.assertContains(response, "Test User")

    def test_index_view_pagination(self):
        """
        Test the pagination behavior of the index view.
        """
        # Create multiple profiles to trigger pagination
        for i in range(15):
            user = User.objects.create_user(
                email=f"test_user{i}@example.com",
                password="password",
            )

            profile = user.profile

            profile.first_name = f"Test{i}"
            profile.last_name = "User"

            self.group.add_member(profile)

        response = self.client.get(reverse("profiles:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/index.html")

        # Check if the page object is paginated correctly
        self.assertIn("page_obj", response.context)

        self.assertIsInstance(response.context["page_obj"], Page)

        # Test second page
        # response = self.client.get(reverse("profiles:index") + "?page=2")
        # self.assertEqual(len(response.context["page_obj"].object_list), 4)

    def test_profile_overview_view(self):
        """
        Test the profile_overview view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_overview",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/profile_overview.html")

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

    def test_edit_involvement_details_get(self):
        """
        Test the edit_involvement_details view renders the form correctly.
        """
        url = reverse(
            "profiles:edit_involvement_details",
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
            "profiles/pages/edit_involvement_details.html",
        )

        # Ensure the form is present in the context
        self.assertIn("involvement_form", response.context)

    def test_edit_involvement_details_view_not_found(self):
        """
        Test the edit_involvement_details view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:edit_involvement_details",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_edit_involvement_details_post_valid(self):
        """
        Test posting valid data to edit_involvement_details view updates the profile.
        """
        url = reverse(
            "profiles:edit_involvement_details",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "is_mentor": True,
            "reason_is_not_mentor": "Valid reason",
            "is_movement_training_facilitator": True,
            "reason_is_not_movement_training_facilitator": "Valid reason",
            "is_skill_training_facilitator": True,
            "reason_is_not_skill_training_facilitator": "Valid reason",
        }

        # Post the data to the view
        response = self.client.post(url, data=data)

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        # Debug: Print the current value of is_mentor to verify the change
        print("is_mentor after post:", self.profile.is_mentor)

        # Check if the profile involvement details were updated
        self.assertTrue(
            self.profile.is_mentor,
            "Profile is_mentor field should be updated",
        )

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            self.profile.get_absolute_url(),
        )

        # Ensure the success message is in the messages
        messages_list = list(response.wsgi_request._messages)
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Profile involvement details updated",
        )

    def test_edit_involvement_details_post_invalid(self):
        """
        Test posting invalid data to edit_involvement_details view does not update the profile.
        """
        url = reverse(
            "profiles:edit_involvement_details",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "is_mentor": "",  # Invalid as it's required by the form
        }
        response = self.client.post(url, data=data)

        # The profile should not be updated
        self.profile.refresh_from_db()
        self.assertNotEqual(
            self.profile.is_mentor,
            "",
        )

        # Check if the response does not redirect
        self.assertEqual(response.status_code, 200)

        # Extract the form from the response context
        form = response.context.get("involvement_form")

        # Ensure the form contains errors
        self.assertIsNotNone(
            form,
            "Form is not present in the response context",
        )
        self.assertTrue(
            form.errors,
            "Form should contain errors",
        )

        # Check for errors in the correct field
        self.assertIn(
            "reason_is_not_mentor",
            form.errors,
            "reason_is_not_mentor field should have errors",
        )
        self.assertIn(
            "This field is required.",
            form.errors["reason_is_not_mentor"],
            "Expected error message not found",
        )

    def test_edit_profile_skills_get(self):
        """
        Test the edit_profile_skills view renders the form correctly.
        """
        url = reverse(
            "profiles:edit_profile_skills",
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
            "profiles/pages/edit_profile_skills.html",
        )

        # Ensure the form is present in the context
        self.assertIn(
            "profile_skills_form",
            response.context,
        )

    def test_edit_profile_skills_post_valid(self):
        """
        Test posting valid data to edit_profile_skills view updates
        the profile's skills and interests.
        """
        skill1 = Skill.objects.create(
            title="Python",
            content="This is a sample content",
            author=self.profile,
        )
        skill2 = Skill.objects.create(
            title="Django",
            content="This is a sample content",
            author=self.profile,
        )
        skill3 = Skill.objects.create(
            title="Web Development",
            content="This is a sample content",
            author=self.profile,
        )
        skill4 = Skill.objects.create(
            title="Data Science",
            content="This is a sample content",
            author=self.profile,
        )

        url = reverse(
            "profiles:edit_profile_skills",
            kwargs={"profile_slug": self.profile.slug},
        )

        data = {
            "skills": [skill1.id, skill2.id],
            "interests": [skill3.id, skill4.id],
        }

        response = self.client.post(url, data=data)

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        # Check if the profile's skills and interests were updated
        self.assertEqual(
            ProfileSkill.objects.filter(
                profile=self.profile,
            ).count(),
            2,
        )
        self.assertEqual(
            ProfileInterest.objects.filter(
                profile=self.profile,
            ).count(),
            2,
        )

        self.assertTrue(
            ProfileSkill.objects.filter(
                profile=self.profile,
                skill=skill1,
            ).exists()
        )
        self.assertTrue(
            ProfileSkill.objects.filter(
                profile=self.profile,
                skill=skill2,
            ).exists()
        )
        self.assertTrue(
            ProfileInterest.objects.filter(
                profile=self.profile, interest=skill3
            ).exists()
        )
        self.assertTrue(
            ProfileInterest.objects.filter(
                profile=self.profile, interest=skill4
            ).exists()
        )

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile.get_absolute_url())

        # Ensure the success message is in the messages
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.profile.get_full_name()}'s profile updated.",
        )

    def test_edit_profile_faith_milestones_get(self):
        """
        Test the GET request to edit_profile_faith_milestones view to
        ensure it renders correctly.
        """
        url = reverse(
            "profiles:edit_profile_faith_milestones",
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
            "profiles/pages/edit_profile_faith_milestones.html",
        )

        # Ensure the faith milestones are in the form's initial data
        form = response.context["profile_faith_milestones_form"]
        self.assertIn(
            "faith_milestones",
            form.initial,
        )

    def test_edit_profile_faith_milestones_post(self):
        """
        Test the POST request to edit_profile_faith_milestones view to
        ensure it updates the profile.
        """
        url = reverse(
            "profiles:edit_profile_faith_milestones",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        data = {
            "faith_milestones": [
                self.faith_milestone_1.id,
                self.faith_milestone_2.id,
            ],
        }
        response = self.client.post(url, data)

        # Check if the response status code is a redirect (after successful POST)
        self.assertEqual(response.status_code, 302)

        # Check if the faith milestones have been updated
        self.assertTrue(
            ProfileFaithMilestone.objects.filter(
                profile=self.profile,
                faith_milestone=self.faith_milestone_1,
            ).exists()
        )

        self.assertTrue(
            ProfileFaithMilestone.objects.filter(
                profile=self.profile,
                faith_milestone=self.faith_milestone_2,
            ).exists()
        )


class TestProfileEncryption(TestCase):
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

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.gender = "male"
        self.profile.date_of_birth = date(2015, 1, 1)
        self.profile.place_of_birth_country = "NG"
        self.profile.place_of_birth_city = "City"

        self.profile.save()

        self.encryption_reason = EncryptionReason.objects.create(
            title="Privacy",
            description="Random description",
            author=self.profile,
        )

    def test_encrypt_profile_post_valid(self):
        """
        Test the POST request to encrypt a profile.
        """
        url = reverse(
            "profiles:encrypt_profile",
            kwargs={"profile_slug": self.profile.slug},
        )

        data = {
            "encryption_reason": self.encryption_reason.pk,
        }
        response = self.client.post(url, data=data)

        # Check if the profile was encrypted
        self.assertTrue(
            ProfileEncryption.objects.filter(
                profile=self.profile,
            ).exists(),
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Profiles name has been hidden from all users",
        )

    def test_gender_based_name_generation(self):
        """
        Test that the correct first name is generated based on profile gender.
        """
        # Set up for a female profile
        self.profile.gender = "female"
        self.profile.save()

        url = reverse(
            "profiles:encrypt_profile",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        # Prepare the data to be sent in the POST request
        data = {
            "encryption_reason": self.encryption_reason.pk,
        }

        # Perform the POST request to trigger the encryption
        response = self.client.post(url, data=data)

        # Ensure the response status is 302 (redirect after successful encryption)
        self.assertEqual(response.status_code, 302)

        # Retrieve the ProfileEncryption object
        profile_encryption = ProfileEncryption.objects.get(
            profile=self.profile,
        )

        # Validate the generated first name
        self.assertTrue(profile_encryption.first_name.isalpha())
        self.assertNotIn(
            "male",
            profile_encryption.first_name.lower(),
        )

    def test_decrypt_profile(self):
        """
        Test the decrypt_profile view to ensure it decrypts the profile correctly.
        """
        # First, encrypt the profile
        self.profile_encryption = ProfileEncryption.objects.create(
            profile=self.profile,
            last_name="Encrypted",
            first_name="Profile",
            encrypted_by=self.profile,
            encryption_reason=self.encryption_reason,
        )

        url = reverse(
            "profiles:decrypt_profile",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the profile was decrypted
        self.assertFalse(
            ProfileEncryption.objects.filter(
                profile=self.profile,
            ).exists()
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Test User's name is now visible to all users",
        )

    def test_encrypt_profile_post_invalid(self):
        """
        Test the POST request to encrypt a profile with invalid data.
        """
        url = reverse(
            "profiles:encrypt_profile",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        # Post with no encryption reason
        data = {}
        response = self.client.post(
            url,
            data=data,
        )

        # The profile should not be encrypted
        self.assertFalse(
            ProfileEncryption.objects.filter(
                profile=self.profile,
            ).exists()
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 200)

    def test_different_author_of_profile_encryption(self):
        """
        Test the decrypt_profile view to ensure it decrypts the profile correctly.
        """

        self.other_user = User.objects.create_user(
            email="otheruser@example.com", password="password"
        )

        self.other_profile = self.other_user.profile

        # First, encrypt the profile
        self.profile_encryption = ProfileEncryption.objects.create(
            profile=self.profile,
            last_name="Encrypted",
            first_name="Profile",
            encrypted_by=self.other_profile,
            encryption_reason=self.encryption_reason,
        )

        url = reverse(
            "profiles:decrypt_profile",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        data = {
            "encryption_reason": self.encryption_reason.pk,
        }

        response = self.client.post(url, data)

        # Check if the response redirects
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You cannot complete this action.",
        )
