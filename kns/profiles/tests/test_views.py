from datetime import date, timedelta

from django.contrib.messages import get_messages
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from kns.classifications.forms import ProfileClassificationForm
from kns.classifications.models import (
    Classification,
    ProfileClassification,
    Subclassification,
)
from kns.core.models import Setting
from kns.custom_user.models import User
from kns.faith_milestones.models import FaithMilestone, ProfileFaithMilestone
from kns.groups.models import Group
from kns.groups.tests import test_constants
from kns.levels.models import Level, ProfileLevel, Sublevel
from kns.mentorships.models import MentorshipArea, ProfileMentorshipArea
from kns.profiles.models import EncryptionReason, ProfileEncryption
from kns.profiles.utils import name_with_apostrophe
from kns.skills.models import ProfileInterest, ProfileSkill, Skill
from kns.vocations.models import ProfileVocation, Vocation


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
        self.profile.is_onboarded = True

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

        # Create Level and ProfileLevel instances
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
        self.classification1 = Classification.objects.create(
            title="Classification 1",
            content="Content for classification 1",
            author=self.profile,
            order=1,
        )
        self.subclassification1 = Subclassification.objects.create(
            title="Subclassification 1",
            content="Content for subclassification 1",
            author=self.profile,
        )

        profile_classification = ProfileClassification.objects.create(
            profile=self.profile,
            classification=self.classification1,
            subclassification=self.subclassification1,
            no=1,
        )

        # Reverse the URL for the profile overview view
        url = reverse(
            "profiles:profile_overview",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        # Make a GET request to the view
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_overview.html",
        )

        # Ensure the profile details are present in the response content
        self.assertIn("Test User", response.content.decode())

        # Check if classifications are present in the context
        self.assertIn("classifications", response.context)
        self.assertEqual(
            response.context["classifications"],
            "Classification 1",
        )

        # Check if subclassifications are present in the context
        self.assertIn("subclassifications", response.context)
        self.assertEqual(
            response.context["subclassifications"],
            "Subclassification 1",
        )

        # Check if profile_classification_no is correctly set
        self.assertIn("profile_classification_no", response.context)
        self.assertEqual(
            response.context["profile_classification_no"],
            profile_classification.no + 1,
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
            "reason_is_not_mentor": (
                "Proin ut ligula vel nunc egestas porttitor. "
                "Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa."
            ),
            "is_movement_training_facilitator": True,
            "reason_is_not_movement_training_facilitator": (
                "Proin ut ligula vel nunc egestas porttitor. "
                "Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa."
            ),
            "is_skill_training_facilitator": True,
            "reason_is_not_skill_training_facilitator": (
                "Proin ut ligula vel nunc egestas porttitor. "
                "Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa."
            ),
        }

        # Post the data to the view
        response = self.client.post(url, data=data)

        # Refresh the profile from the database
        self.profile.refresh_from_db()

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

    def test_edit_profile_level_get(self):
        """
        Test the edit_profile_level view renders the form correctly on GET request.
        """
        url = reverse(
            "profiles:edit_profile_level",
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
            "profiles/pages/edit_profile_level.html",
        )

        # Ensure the form is present in the context
        self.assertIn("profile_level_form", response.context)

    def test_edit_profile_level_post_valid(self):
        """
        Test the edit_profile_level view processes and saves valid
        data correctly on POST request.
        """
        url = reverse(
            "profiles:edit_profile_level",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        data = {
            "level": self.level1.id,
            "sublevel": self.sublevel1.id,
        }

        response = self.client.post(url, data)

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)

        # Use filter instead of get, and ensure there's only one object
        profile_levels = ProfileLevel.objects.filter(
            profile=self.profile,
            level=self.level1,
            sublevel=self.sublevel1,
        )

        # Ensure only one ProfileLevel exists for the profile
        self.assertEqual(profile_levels.count(), 1)

        profile_level = profile_levels.first()

        self.assertEqual(profile_level.level, self.level1)
        self.assertEqual(profile_level.sublevel, self.sublevel1)

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Level updated successfully.",
        )

    def test_edit_profile_level_post_no_sublevel(self):
        """
        Test the edit_profile_level view when the selected level has no
        sublevels and sublevel is set to 'null'.
        """
        url = reverse(
            "profiles:edit_profile_level",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        # Ensure no existing ProfileLevel objects for the profile and level
        ProfileLevel.objects.filter(profile=self.profile, level=self.level1).delete()

        data = {
            "level": self.level1.id,
            "sublevel": "null",
        }
        response = self.client.post(url, data)

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)

        # Use filter instead of get to handle multiple objects
        profile_levels = ProfileLevel.objects.filter(
            profile=self.profile, level=self.level1
        )

        # Ensure only one ProfileLevel exists for the profile with the given level
        self.assertEqual(profile_levels.count(), 1)

        profile_level = profile_levels.first()

        self.assertEqual(profile_level.level, self.level1)
        self.assertIsNone(profile_level.sublevel)

        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Level updated successfully.")

    def test_edit_profile_level_post_invalid_level(self):
        """
        Test the edit_profile_level view with invalid level data.
        """
        url = reverse(
            "profiles:edit_profile_level",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "level": "invalid",
            "sublevel": "invalid",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        # Ensure no ProfileLevel was created
        self.assertFalse(
            ProfileLevel.objects.filter(
                profile=self.profile,
            ).exists(),
        )

        # Check for error message in messages
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Invalid level ID.",
        )

    def test_edit_profile_level_post_missing_level(self):
        """
        Test the edit_profile_level view when no level is provided.
        """
        url = reverse(
            "profiles:edit_profile_level",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "sublevel": self.sublevel1.id,
        }
        response = self.client.post(url, data)

        # Check if the response status code is 400 as expected
        self.assertEqual(response.status_code, 400)

        # Ensure no ProfileLevel was created
        self.assertFalse(
            ProfileLevel.objects.filter(profile=self.profile).exists(),
        )

    def test_profile_levels_view_no_profile_found(self):
        """
        Test the profile_levels view when a non-existent profile is requested.
        """
        self.profile_level1 = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level1,
            created_at=timezone.now() - timedelta(days=10),
        )
        self.profile_level2 = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level2,
            created_at=timezone.now() - timedelta(days=5),
        )

        url = reverse(
            "profiles:profile_levels",
            kwargs={
                "profile_slug": "non-existent",
            },
        )

        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_profile_levels_view_no_levels(self):
        """
        Test the profile_levels view when the profile has no levels.
        """
        self.profile_level1 = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level1,
            created_at=timezone.now() - timedelta(days=10),
        )
        self.profile_level2 = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level2,
            created_at=timezone.now() - timedelta(days=5),
        )

        # Create a profile with no levels
        user_without_levels = User.objects.create_user(
            email="nolevels@example.com",
            password="password",
        )
        profile_without_levels = user_without_levels.profile

        url = reverse(
            "profiles:profile_levels",
            kwargs={
                "profile_slug": profile_without_levels.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if 'profile_levels' is in context and is empty
        self.assertIn("profile_levels", response.context)
        self.assertQuerySetEqual(
            response.context["profile_levels"],
            [],
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

        self.profile.is_onboarded = True
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


class TestEditProfileVocationsView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and log them in
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        # Create a profile
        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.slug = "test-user"

        self.profile.save()

        # Create vocations
        self.vocation1 = Vocation.objects.create(
            title="Teacher",
            description="Teaches students.",
            author=self.profile,
        )
        self.vocation2 = Vocation.objects.create(
            title="Engineer",
            description="Builds systems.",
            author=self.profile,
        )
        self.vocation3 = Vocation.objects.create(
            title="Doctor",
            description="Provides medical care.",
            author=self.profile,
        )

        # Add one vocation to the profile
        self.profile_vocation = ProfileVocation.objects.create(
            profile=self.profile,
            vocation=self.vocation1,
        )

    def test_edit_profile_vocations_view_loads_correctly(self):
        """
        Test that the view loads correctly and displays the form with initial data.
        """
        url = reverse(
            "profiles:edit_profile_vocations",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the form is in the context and that vocation1 is preselected
        self.assertIn("profile_vocations_form", response.context)

        form = response.context["profile_vocations_form"]

        # Compare vocation IDs instead of objects
        self.assertIn(self.vocation1.id, form.initial["vocations"])

    def test_edit_profile_vocations_view_valid_post(self):
        """
        Test that submitting valid data updates the profile's vocations correctly.
        """
        url = reverse(
            "profiles:edit_profile_vocations",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        form_data = {
            "vocations": [self.vocation2.id, self.vocation3.id],
        }

        response = self.client.post(url, data=form_data)

        # Check if the response redirects to the profile page
        self.assertEqual(response.status_code, 302)

        # Check if the profile vocations were updated
        updated_vocations = ProfileVocation.objects.filter(
            profile=self.profile,
        )
        self.assertEqual(updated_vocations.count(), 2)
        self.assertTrue(
            ProfileVocation.objects.filter(
                profile=self.profile,
                vocation=self.vocation2,
            ).exists()
        )
        self.assertTrue(
            ProfileVocation.objects.filter(
                profile=self.profile,
                vocation=self.vocation3,
            ).exists()
        )

        # Check if a success message is shown
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Test User's profile updated.",
        )

    def test_edit_profile_vocations_view_invalid_post(self):
        """
        Test that submitting invalid data does not update the profile's vocations.
        """
        url = reverse(
            "profiles:edit_profile_vocations",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        form_data = {
            "vocations": [],  # Invalid: no vocations selected
        }

        response = self.client.post(url, data=form_data)

        # Check that the form is invalid and rendered again
        self.assertEqual(response.status_code, 200)

        # Check that no vocations were updated (still only one vocation)
        updated_vocations = ProfileVocation.objects.filter(
            profile=self.profile,
        )
        self.assertEqual(updated_vocations.count(), 1)

    def test_edit_profile_vocations_view_vocation_removal(self):
        """
        Test that previously selected vocations are removed if not submitted.
        """
        url = reverse(
            "profiles:edit_profile_vocations",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        form_data = {
            "vocations": [self.vocation2.id],
        }

        response = self.client.post(
            url,
            data=form_data,
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 302)

        # Check if only vocation2 remains
        updated_vocations = ProfileVocation.objects.filter(
            profile=self.profile,
        )

        self.assertEqual(updated_vocations.count(), 1)
        self.assertTrue(
            ProfileVocation.objects.filter(
                profile=self.profile,
                vocation=self.vocation2,
            ).exists()
        )
        self.assertFalse(
            ProfileVocation.objects.filter(
                profile=self.profile,
                vocation=self.vocation1,
            ).exists()
        )


class EditProfileClassificationsTests(TestCase):
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

        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        # Create classifications and subclassifications
        self.classification1 = Classification.objects.create(
            title="Classification 1",
            content="Content for classification 1",
            author=self.profile,
            order=1,
        )
        self.subclassification1 = Subclassification.objects.create(
            title="Subclassification 1",
            content="Content for subclassification 1",
            author=self.profile,
        )

        # Create a profile classification
        self.profile_classification = ProfileClassification.objects.create(
            profile=self.profile,
            classification=self.classification1,
            subclassification=self.subclassification1,
            no=1,
        )

    def test_get_edit_profile_classifications(self):
        url = reverse(
            "profiles:edit_profile_classifications",
            kwargs={
                "profile_slug": self.profile.slug,
                "profile_classification_no": 1,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "classifications/pages/edit_profile_classifications.html",
        )

        self.assertIn(
            "profile_classifications_form",
            response.context,
        )
        self.assertIsInstance(
            response.context["profile_classifications_form"],
            ProfileClassificationForm,
        )
        self.assertEqual(
            response.context["profile_classification_no"],
            self.profile_classification.no,
        )

    def test_post_create_profile_classification(self):
        url = reverse(
            "profiles:edit_profile_classifications",
            kwargs={
                "profile_slug": self.profile.slug,
                "profile_classification_no": 2,
            },
        )

        data = {
            "classification": self.classification1.id,
            "subclassification": self.subclassification1.id,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "classifications/pages/edit_profile_classifications.html",
        )

        # Check if the new profile classification was created
        new_profile_classification = ProfileClassification.objects.get(
            profile=self.profile,
            no=2,
        )

        self.assertEqual(
            new_profile_classification.classification,
            self.classification1,
        )
        self.assertEqual(
            new_profile_classification.subclassification,
            self.subclassification1,
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(
            str(messages[0]),
            "Classification updated successfully.",
        )

    def test_post_duplicate_profile_classification(self):
        url = reverse(
            "profiles:edit_profile_classifications",
            kwargs={
                "profile_slug": self.profile.slug,
                "profile_classification_no": self.profile_classification.no,
            },
        )
        data = {
            "classification": self.classification1.id,
            "subclassification": self.subclassification1.id,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "classifications/pages/edit_profile_classifications.html",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "A similar classification has already been assigned to this user",
        )

    def test_post_without_subclassification(self):
        url = reverse(
            "profiles:edit_profile_classifications",
            kwargs={
                "profile_slug": self.profile.slug,
                "profile_classification_no": 2,
            },
        )
        data = {
            "classification": self.classification1.id,
            "subclassification": "",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "classifications/pages/edit_profile_classifications.html",
        )

        # Check if the new profile classification was created without subclassification
        new_profile_classification = ProfileClassification.objects.get(
            profile=self.profile,
            no=2,
        )
        self.assertEqual(
            new_profile_classification.classification,
            self.classification1,
        )
        self.assertIsNone(
            new_profile_classification.subclassification,
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Classification updated successfully.",
        )


class TestProfileMentorshipsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.slug = "test-user"

        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )
        self.other_user.save()
        self.other_profile = self.other_user.profile

        # Create some mentorship areas for testing
        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="Mentorship in Software Engineering.",
            author=self.profile,
            status="published",
        )
        self.mentorship_area2 = MentorshipArea.objects.create(
            title="Data Science",
            content="Mentorship in Data Science.",
            author=self.profile,
            status="published",
        )

    def test_profile_mentorships_view_loads_correctly(self):
        """
        Test that the profile_mentorships view loads correctly
        and renders the page.
        """
        url = reverse(
            "profiles:profile_mentorships",
            kwargs={"profile_slug": self.profile.slug},
        )
        response = self.client.get(url)

        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area2,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "mentorships/pages/profile_mentorships_page.html",
        )
        # Add more checks based on the expected context or content
        self.assertIn("profile", response.context)

        self.assertEqual(response.context["profile"], self.profile)
        self.assertEqual(response.context["profile"].mentorship_areas.count(), 2)

    def test_profile_mentorships_view_with_invalid_slug(self):
        """
        Test that the profile_mentorships view returns a 404 error
        when the profile slug does not exist.
        """
        url = reverse(
            "profiles:profile_mentorships",
            kwargs={"profile_slug": "invalid-slug"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TestEditProfileMentorshipAreasView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.slug = "test-user"

        self.profile.save()

        # Create mentorship areas for testing
        self.mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="Mentorship in Software Engineering.",
            author=self.profile,
            status="published",
        )
        self.mentorship_area2 = MentorshipArea.objects.create(
            title="Data Science",
            content="Mentorship in Data Science.",
            author=self.profile,
            status="published",
        )

        # Create initial ProfileMentorshipArea associations
        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area,
        )
        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=self.mentorship_area2,
        )

    def test_edit_profile_mentorship_areas_view_loads_correctly(self):
        """
        Test that the edit_profile_mentorship_areas view loads correctly
        and renders the page with the correct initial data.
        """
        url = reverse(
            "profiles:edit_profile_mentorship_areas",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "mentorships/pages/edit_profile_mentorships.html",
        )
        self.assertIn(
            "profile_mentorship_areas_form",
            response.context,
        )
        form = response.context["profile_mentorship_areas_form"]
        self.assertTrue(
            form.initial["mentorship_areas"],
            [self.mentorship_area.id, self.mentorship_area2.id],
        )

    def test_edit_profile_mentorship_areas_form_submission(self):
        """
        Test that submitting the form in the edit_profile_mentorship_areas view
        updates the profile mentorship areas correctly.
        """
        url = reverse(
            "profiles:edit_profile_mentorship_areas",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        new_mentorship_area = MentorshipArea.objects.create(
            title="Machine Learning",
            content="Mentorship in Machine Learning.",
            author=self.profile,
            status="published",
        )

        response = self.client.post(
            url,
            data={
                "mentorship_areas": [
                    self.mentorship_area.id,
                    new_mentorship_area.id,
                ],
            },
        )

        # Check if the profile mentorship areas have been updated
        self.assertEqual(
            ProfileMentorshipArea.objects.filter(profile=self.profile).count(),
            2,
        )
        self.assertTrue(
            ProfileMentorshipArea.objects.filter(
                profile=self.profile, mentorship_area=new_mentorship_area
            ).exists()
        )

        # Check for success message
        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            (
                f"{name_with_apostrophe(self.profile.get_full_name())} "
                "mentorship areas have been updated"
            ),
        )

        # Check redirection
        self.assertRedirects(
            response,
            reverse(
                "profiles:profile_mentorships",
                kwargs={
                    "profile_slug": self.profile.slug,
                },
            ),
        )

    def test_edit_profile_mentorship_areas_view_with_invalid_slug(self):
        """
        Test that the view returns a 404 error when the profile slug does not exist.
        """
        url = reverse(
            "profiles:edit_profile_mentorship_areas",
            kwargs={
                "profile_slug": "invalid-slug",
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_edit_profile_mentorship_areas_form_invalid_data(self):
        """
        Test that submitting invalid form data does not update the
        profile mentorship areas and stays on the same page.
        """
        url = reverse(
            "profiles:edit_profile_mentorship_areas",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        response = self.client.post(
            url,
            data={
                "mentorship_areas": [],  # Invalid data
            },
        )

        # Check that the profile mentorship areas have not been updated
        self.assertEqual(
            ProfileMentorshipArea.objects.filter(profile=self.profile).count(),
            2,
        )

        # Check for form errors
        self.assertEqual(response.status_code, 200)

        form = response.context["profile_mentorship_areas_form"]

        self.assertFalse(form.is_valid())


class TestIndexView(TestCase):
    def setUp(self):
        """
        Set up test data for the index view.
        """
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpassword",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile1 = self.user.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        self.profile1.is_onboarded = True
        self.profile1.first_name = "John"
        self.profile1.last_name = "Doe"
        self.profile1.gender = "male"
        self.profile1.role = "leader"
        self.profile1.place_of_birth_country = "US"
        self.profile1.place_of_birth_city = "New York"
        self.profile1.location_country = "US"
        self.profile1.location_city = "Los Angeles"
        self.profile1.save()

        self.profile2.first_name = "Jane"
        self.profile2.last_name = "Smith"
        self.profile2.role = "member"
        self.profile2.gender = "female"
        self.profile2.place_of_birth_country = "CA"
        self.profile2.place_of_birth_city = "Toronto"
        self.profile2.location_country = "CA"
        self.profile2.location_city = "Vancouver"
        self.profile2.save()

        self.profile3.first_name = "Jack"
        self.profile3.last_name = "Reacher"
        self.profile3.role = "member"
        self.profile3.gender = "male"
        self.profile3.date_of_birth = "2002-08-08"
        self.profile3.place_of_birth_country = "US"
        self.profile3.place_of_birth_city = "San Francisco"
        self.profile3.location_country = "US"
        self.profile3.location_city = "San Diego"
        self.profile3.save()

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile1,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.group.add_member(self.profile2)
        self.group.add_member(self.profile3)

    def test_view_filters_by_gender(self):
        """
        Test that profiles can be filtered by gender.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "gender": "female",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_renders_correct_template(self):
        """
        Test that the index view renders the correct template.
        """

        response = self.client.get(reverse("profiles:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "profiles/pages/index.html",
        )

    def test_view_filters_by_role(self):
        """
        Test that profiles can be filtered by role.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "role": "leader",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_min_age(self):
        """
        Test that profiles can be filtered by minimum age.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "min_age": 30,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jack Reacher")

    def test_pagination(self):
        """
        Test that pagination works correctly when more profiles exist.
        """
        # Create more profiles to trigger pagination
        for i in range(15):
            user_instance = User.objects.create_user(
                email=f"user{i}@example.com",
                password="password",
            )

            profile_instance = user_instance.profile

            profile_instance.first_name = f"Firstname {i}"
            profile_instance.last_name = f"Lastname {i}"

        response = self.client.get(reverse("profiles:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["page_obj"]),
            3,
        )

        # Test second page
        response = self.client.get(
            reverse("profiles:index"),
            {
                "page": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_empty_form_does_not_filter(self):
        """
        Test that an empty form does not apply any filters.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")

    def test_view_filters_by_place_of_birth_country(self):
        """
        Test that profiles can be filtered by place of birth country.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "place_of_birth_country": "US",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jack Reacher")
        self.assertNotContains(response, "Jane Smith")

    def test_view_filters_by_place_of_birth_city(self):
        """
        Test that profiles can be filtered by place of birth city.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "place_of_birth_city": "San Francisco",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jack Reacher")
        self.assertNotContains(response, "Jane Smith")

    def test_view_filters_by_location_country(self):
        """
        Test that profiles can be filtered by location country.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "location_country": "CA",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_location_city(self):
        """
        Test that profiles can be filtered by location city.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "location_city": "Vancouver",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_is_movement_training_facilitator(self):
        """
        Test that profiles can be filtered by 'movement training facilitator' status.
        """
        # Set the 'is_movement_training_facilitator' status
        self.profile1.is_movement_training_facilitator = True
        self.profile1.save()

        response = self.client.get(
            reverse("profiles:index"),
            {
                "is_movement_training_facilitator": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_is_skill_training_facilitator(self):
        """
        Test that profiles can be filtered by 'skill training facilitator' status.
        """
        # Set the 'is_skill_training_facilitator' status
        self.profile2.is_skill_training_facilitator = True
        self.profile2.save()

        response = self.client.get(
            reverse("profiles:index"),
            {
                "is_skill_training_facilitator": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_is_mentor(self):
        """
        Test that profiles can be filtered by 'mentor' status.
        """
        # Set the 'is_mentor' status
        self.profile1.is_mentor = True
        self.profile1.save()

        response = self.client.get(
            reverse("profiles:index"),
            {
                "is_mentor": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_filters_by_skills(self):
        """
        Test that profiles can be filtered by skills.
        """
        # Assign skills to profiles
        skill = Skill.objects.create(
            title="Leadership",
            content="Leadership skill",
            author=self.profile1,
        )

        ProfileSkill.objects.create(
            skill=skill,
            profile=self.profile2,
        )

        response = self.client.get(
            reverse("profiles:index"),
            {
                "skills": [skill.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile2.get_full_name())
        self.assertNotContains(response, self.profile3.get_full_name())

    def test_view_filters_by_interests(self):
        """
        Test that profiles can be filtered by interests.
        """
        # Assign interests to profiles
        interest = Skill.objects.create(
            title="Running",
            content="Running interest",
            author=self.profile1,
        )

        ProfileInterest.objects.create(
            interest=interest,
            profile=self.profile2,
        )

        response = self.client.get(
            reverse("profiles:index"),
            {
                "interests": [interest.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile2.get_full_name())
        self.assertNotContains(response, self.profile3.get_full_name())

    def test_view_filters_by_vocations(self):
        """
        Test that profiles can be filtered by vocations.
        """
        # Assign vocations to profiles
        vocation = Vocation.objects.create(
            title="Engineering",
            description="Engineering vocation",
            author=self.profile1,
        )

        ProfileVocation.objects.create(
            vocation=vocation,
            profile=self.profile2,
        )

        response = self.client.get(
            reverse("profiles:index"),
            {
                "vocations": [vocation.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile2.get_full_name())
        self.assertNotContains(response, self.profile3.get_full_name())

    def test_view_filters_by_mentorship_areas(self):
        """
        Test that profiles can be filtered by mentorship areas.
        """
        # Create mentorship areas
        mentorship_area1 = MentorshipArea.objects.create(
            title="Area 1",
            content="Description for mentorship area 1",
            author=self.profile1,
        )
        mentorship_area2 = MentorshipArea.objects.create(
            title="Area 2",
            content="Description for mentorship area 2",
            author=self.profile1,
        )

        # Assign mentorship areas to profiles
        ProfileMentorshipArea.objects.create(
            mentorship_area=mentorship_area1,
            profile=self.profile1,
        )
        ProfileMentorshipArea.objects.create(
            mentorship_area=mentorship_area2,
            profile=self.profile2,
        )

        response = self.client.get(
            reverse("profiles:index"),
            {
                "mentorship_areas": [mentorship_area1.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")

    def test_view_filters_by_faith_milestones(self):
        """
        Test that profiles can be filtered by faith milestones.
        """
        # Create faith milestones
        faith_milestone1 = FaithMilestone.objects.create(
            title="Milestone 1",
            type="profile",
            description="First faith milestone",
            author=self.profile1,
        )
        faith_milestone2 = FaithMilestone.objects.create(
            title="Milestone 2",
            type="profile",
            description="Second faith milestone",
            author=self.profile1,
        )

        # Assign faith milestones to profiles
        ProfileFaithMilestone.objects.create(
            faith_milestone=faith_milestone1,
            profile=self.profile1,
        )
        ProfileFaithMilestone.objects.create(
            faith_milestone=faith_milestone2,
            profile=self.profile2,
        )

        response = self.client.get(
            reverse("profiles:index"),
            {
                "faith_milestones": [faith_milestone1.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile1.get_full_name())
        self.assertNotContains(response, self.profile2.get_full_name())
        self.assertNotContains(response, self.profile3.get_full_name())

    def test_view_no_filters(self):
        """
        Test that the view displays all profiles when no filters are applied.
        """
        response = self.client.get(reverse("profiles:index"))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")
        self.assertContains(response, "Jack Reacher")

    def test_view_search_by_first_name(self):
        """
        Test that profiles can be searched by first name.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "search": "Jane",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")

    def test_view_search_by_last_name(self):
        """
        Test that profiles can be searched by last name.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "search": "Reacher",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jack Reacher")
        self.assertNotContains(response, "Jane Smith")

    def test_view_search_by_full_name(self):
        """
        Test that profiles can be searched by full name.
        """
        response = self.client.get(
            reverse("profiles:index"),
            {
                "search": "John Doe",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")
        self.assertNotContains(response, "Jack Reacher")


class TestMakeLeaderPageView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Origin group",
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        self.other_user.verified = True
        self.other_user.agreed_to_terms = True

        self.other_user.save()

        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Doe"
        self.other_profile.gender = "Male"
        self.other_profile.date_of_birth = "1990-01-01"
        self.other_profile.place_of_birth_country = "US"
        self.other_profile.place_of_birth_city = "New York"
        self.other_profile.location_country = "US"
        self.other_profile.location_city = "New York"
        self.other_profile.role = "member"

        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_leader_page_loads_correctly(self):
        """
        Test that the make_leader_page view loads correctly.
        """

        url = reverse(
            "profiles:make_leader_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "profiles/pages/make_leader.html",
        )

        self.assertIn("profile", response.context)

    def test_make_leader_page_with_invalid_slug(self):
        """
        Test that the make_leader_page returns a 404 error for an invalid slug.
        """

        url = reverse(
            "profiles:make_leader_page",
            kwargs={
                "profile_slug": "invalid-slug",
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_make_leader_page_without_permission(self):
        """
        Test that the make_leader_page redirects if user is not a group leader.
        """

        self.group.members.all().delete()

        url = reverse(
            "profiles:make_leader_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertRedirects(response, self.other_profile.get_absolute_url())

        self.assertEqual(response.status_code, 302)

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()} "
                "to perform this action."
            ),
        )

    def test_make_leader_page_not_group_leader(self):
        """
        Test that the make_leader_page redirects if user is not a group leader.
        """

        self.group.leader = self.other_profile
        self.group.save()

        url = reverse(
            "profiles:make_leader_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertRedirects(response, self.other_profile.get_absolute_url())

        self.assertEqual(response.status_code, 302)


class TestMakeLeaderView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Origin group",
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        self.other_user.verified = True
        self.other_user.agreed_to_terms = True

        self.other_user.save()

        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Doe"
        self.other_profile.gender = "Male"
        self.other_profile.date_of_birth = "1990-01-01"
        self.other_profile.place_of_birth_country = "US"
        self.other_profile.place_of_birth_city = "New York"
        self.other_profile.location_country = "US"
        self.other_profile.location_city = "New York"
        self.other_profile.role = "member"

        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_leader_success(self):
        """
        Test that a profile is successfully promoted to leader.
        """

        url = reverse(
            "profiles:make_leader",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Refresh the profile after the change
        self.other_profile.refresh_from_db()

        self.assertEqual(
            self.other_profile.role,
            "leader",
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(
            len(messages),
            1,
        )
        self.assertEqual(
            str(messages[0]),
            f"{self.other_profile.get_full_name()} has been successfully promoted to a leader.",
        )

    def test_make_leader_without_permission(self):
        """
        Test that the make_leader view redirects if user is not a group leader.
        """

        self.group.members.all().delete()

        url = reverse(
            "profiles:make_leader",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.post(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()}"
                " to perform this action."
            ),
        )

    def test_make_leader_not_eligible(self):
        """Test that the make_leader view returns an error if the profile is not eligible."""
        # Simulate that the other profile is not eligible to become a leader
        self.other_profile.role = "leader"
        self.other_profile.save()

        url = reverse(
            "profiles:make_leader",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.post(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.other_profile.get_full_name()} is not eligible to become a leader.",
        )


class TestMakeMemberPageView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Origin group",
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )
        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Wayne"

        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_member_page_loads_correctly(self):
        """
        Test that the make_member_page view loads correctly.
        """

        url = reverse(
            "profiles:make_member_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "profiles/pages/make_member.html",
        )

        self.assertIn("profile", response.context)

    def test_make_member_page_with_invalid_slug(self):
        """Test that the make_member_page returns a 404 error for an invalid slug."""
        url = reverse(
            "profiles:make_member_page", kwargs={"profile_slug": "invalid-slug"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_make_member_page_without_permission(self):
        """Test that the make_member_page redirects if user is not a group leader."""

        self.group.members.all().delete()

        url = reverse(
            "profiles:make_member_page",
            kwargs={"profile_slug": self.other_profile.slug},
        )
        response = self.client.get(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()}"
                " to perform this action."
            ),
        )


class TestMakeMemberView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Origin group",
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )
        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Wayne"

        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_member_success(self):
        """Test that a profile is successfully demoted to member."""
        self.other_profile.role = "leader"
        self.other_profile.save()

        url = reverse(
            "profiles:make_member",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Refresh the profile after the change
        self.other_profile.refresh_from_db()

        # Assert the role has changed
        self.assertEqual(
            self.other_profile.role,
            "member",
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"{name_with_apostrophe(self.other_profile.get_full_name())}"
                " role has been changed to a member."
            ),
        )

    def test_make_member_without_permission(self):
        """Test that the make_member view redirects if user is not a group leader."""
        url = reverse(
            "profiles:make_member",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        self.group.members.all().delete()

        response = self.client.post(url)

        self.assertRedirects(response, self.other_profile.get_absolute_url())

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()}"
                " to perform this action."
            ),
        )

    def test_make_member_not_eligible(self):
        """
        Test that the make_member view returns an error if the profile is not eligible.
        """

        self.other_profile.role = "member"
        self.other_profile.save()

        url = reverse(
            "profiles:make_member",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.post(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.other_profile.get_full_name()} is not eligible to become a member.",
        )


class TestMakeExternalPersonPageView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.is_onboarded = True
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Origin group",
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )
        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Wayne"
        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_external_person_page_loads_correctly(self):
        """
        Test that the make_external_person_page view loads correctly.
        """
        url = reverse(
            "profiles:make_external_person_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "profiles/pages/make_external_person.html",
        )

        self.assertIn(
            "profile",
            response.context,
        )

    def test_make_external_person_page_with_invalid_slug(self):
        """
        Test that the make_external_person_page returns a 404 error for an invalid slug.
        """
        url = reverse(
            "profiles:make_external_person_page",
            kwargs={
                "profile_slug": "invalid-slug",
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_make_external_person_page_without_permission(self):
        """
        Test that the make_external_person_page redirects if user is not a group leader.
        """

        self.group.members.all().delete()

        url = reverse(
            "profiles:make_external_person_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()} "
                "to perform this action."
            ),
        )

    def test_make_external_person_page_for_non_group_member(self):
        """
        Test that the make_external_person_page redirects if the target profile is not
        a member of the requesting user's group.
        """
        other_group = Group.objects.create(
            leader=self.other_profile,
            name="Other group",
            location_country="US",
            location_city="New York",
            slug="other-group",
            description="A different group",
        )

        self.group.members.all().delete()
        other_group.add_member(self.other_profile)

        url = reverse(
            "profiles:make_external_person_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()} "
                "to perform this action."
            ),
        )

    def test_make_external_person_page_for_non_group_leader_user(self):
        """
        Test that the make_external_person_page redirects if the user profile is not
        a leader of a group.
        """
        self.group.leader = self.other_profile
        self.group.save()

        url = reverse(
            "profiles:make_external_person_page",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.get(url)

        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 0)


class TestMakeExternalPersonView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testleader@example.com",
            password="testpassword",
        )
        self.client.login(
            email="testleader@example.com",
            password="testpassword",
        )

        # Set up the leader profile and group
        self.leader_profile = self.user.profile
        self.leader_profile.role = "leader"
        self.leader_profile.is_onboarded = True
        self.leader_profile.first_name = "Leader"
        self.leader_profile.last_name = "Profile"
        self.leader_profile.save()

        self.group = Group.objects.create(
            leader=self.leader_profile,
            name="Test Group",
            location_country="NG",
            location_city="Bauchi",
            slug="test-group",
            description="Group description",
        )

        # Set up another profile in the group
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        self.other_user.verified = True
        self.other_user.agreed_to_terms = True
        self.other_user.save()

        self.other_profile = self.other_user.profile

        self.other_profile.first_name = "John"
        self.other_profile.last_name = "Doe"
        self.other_profile.gender = "Male"
        self.other_profile.date_of_birth = "1990-01-01"
        self.other_profile.place_of_birth_country = "US"
        self.other_profile.place_of_birth_city = "New York"
        self.other_profile.location_country = "US"
        self.other_profile.location_city = "New York"
        self.other_profile.role = "member"

        self.other_profile.save()

        self.group.add_member(self.other_profile)

    def test_make_external_person_success(self):
        """
        Test that a profile is successfully changed to an external person.
        """

        url = reverse(
            "profiles:make_external_person",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        # Assert the redirect to the profile detail page
        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Refresh the profile to reflect the changes
        self.other_profile.refresh_from_db()

        # Assert the role has been changed to external person
        self.assertEqual(
            self.other_profile.role,
            "external_person",
        )

        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.other_profile.get_full_name()} is now an external person.",
        )

    def test_make_external_person_without_permission(self):
        """
        Test that the view redirects if the user is not a group leader.
        """

        # Log in as another user who is not the leader
        other_user = User.objects.create_user(
            email="unauthorized@example.com",
            password="password",
        )

        other_user.profile.is_onboarded = True
        other_user.profile.save()

        self.client.login(
            email="unauthorized@example.com",
            password="password",
        )

        url = reverse(
            "profiles:make_external_person",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        # Assert the redirect back to the profile page
        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for the error message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 0)

    def test_make_external_person_not_eligible(self):
        """Test that the view returns an error if the profile cannot become an external person."""
        # Make the profile ineligible to become an external person
        self.other_profile.role = "external_person"
        self.other_profile.save()

        url = reverse(
            "profiles:make_external_person",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        # Assert the redirect to the profile detail page
        self.assertRedirects(response, self.other_profile.get_absolute_url())

        # Check for the error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.other_profile.get_full_name()} is not eligible to become an external person.",
        )

    def test_make_external_person_not_leader_of_external_person(self):
        """
        Test that the view returns an error if the profile cannot become an
        external person.
        """
        # Make the profile ineligible to become an external person
        self.group.members.all().delete()

        url = reverse(
            "profiles:make_external_person",
            kwargs={
                "profile_slug": self.other_profile.slug,
            },
        )

        response = self.client.post(url)

        # Assert the redirect to the profile detail page
        self.assertRedirects(
            response,
            self.other_profile.get_absolute_url(),
        )

        # Check for the error message
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            (
                f"You must be the leader of {self.other_profile.get_full_name()} "
                "to perform this action."
            ),
        )
