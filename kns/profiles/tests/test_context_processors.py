from unittest.mock import patch

from django.http import Http404
from django.test import RequestFactory, TestCase

from kns.custom_user.models import User
from kns.groups.models import Group, GroupMember
from kns.groups.tests.factories import GroupFactory
from kns.profiles.context_processors import profile_context, user_profile_context
from kns.profiles.models import Profile


class ContextProcessorsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
        )
        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.save()

        self.group = GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
            leader=self.profile,
        )

        self.group_member = GroupMember.objects.create(
            group=self.group,
            profile=self.profile,
        )

    def test_user_profile_context_authenticated_user_with_profile(self):
        request = self.factory.get("/")
        request.user = self.user

        context = user_profile_context(request)

        self.assertIn("my_profile", context)
        self.assertEqual(context["my_profile"], self.profile)

    def test_user_profile_context_authenticated_user_without_profile(self):
        request = self.factory.get("/")

        new_user = User.objects.create_user(
            email="newuser@example.com",
            password="newpass",
        )

        # If the profile is automatically created, delete it
        if hasattr(new_user, "profile"):
            new_user.profile.delete()

        request.user = new_user

        context = user_profile_context(request)

        self.assertIn("my_profile", context)

    def test_profile_context_profile_does_not_exist(self):
        request = self.factory.get("/")
        request.user = self.user

        # Mock the get_profile_slug function to return a non-existent slug
        with patch(
            "kns.profiles.context_processors.get_profile_slug",
            return_value="nonexistent",
        ):
            with self.assertRaises(Http404):
                profile_context(request)
