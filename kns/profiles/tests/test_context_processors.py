from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from kns.custom_user.models import User
from kns.groups.models import GroupMember
from kns.groups.tests.factories import GroupFactory
from kns.profiles.context_processors import profile_context


class TestContextProcessors(TestCase):
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

    def test_profile_context_profile_does_not_exist(self):
        request = self.factory.get("/")
        request.user = self.user

        # Mock the resolver_match attribute
        request.resolver_match = MagicMock()
        request.resolver_match.kwargs = {
            "slug": "nonexistent",
        }

        # Mock the get_profile_slug function to return a non-existent slug
        with patch(
            "kns.profiles.utils.get_profile_slug",
            return_value="nonexistent",
        ):
            context = profile_context(request)
            # Check if the profile is None or the profile_settings_form
            #  is None
            self.assertIsNone(context["profile"])
            self.assertIsNone(context["profile_settings_form"])
