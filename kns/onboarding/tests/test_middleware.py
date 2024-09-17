# from django.urls import reverse
# from django.test import RequestFactory, TestCase
# from django.http import HttpResponse
# from unittest.mock import MagicMock, patch

# from kns.profiles.models import Profile
# from kns.onboarding.models import ProfileOnboarding
# from kns.custom_user.models import User
# from kns.groups.models import GroupMember
# from kns.groups.tests.factories import GroupFactory
# from kns.onboarding.middleware import OnboardingMiddleware


# # class OnboardingMiddlewareTestCase(TestCase):
# #     def setUp(self):
# #         self.factory = RequestFactory()
# #         self.middleware = OnboardingMiddleware(lambda request: HttpResponse(""))

# #         self.user = User.objects.create_user(
# #             email="testuser@example.com",
# #             password="testpass",
# #         )
# #         self.profile = self.user.profile
# #         self.profile.role = "leader"
# #         self.profile.save()

# #         self.group = GroupFactory(
# #             name="Bible Study Group",
# #             location_country="Nigeria",
# #             location_city="Lagos",
# #             leader=self.profile,
# #         )

# #         self.group_member = GroupMember.objects.create(
# #             group=self.group,
# #             profile=self.profile,
# #         )

# #     def test_redirect_to_onboarding_step(self):
# #         # Test redirection when user is not onboarded
# #         self.profile.is_onboarded = False
# #         self.profile.save()

# #         request = self.factory.get("/profiles/")
# #         request.user = self.user

# #         # Mock get_current_step to return a specific step
# #         with patch(
# #             "kns.onboarding.models.ProfileOnboarding.get_current_step",
# #             return_value={"url_name": "onboarding:step1"},
# #         ):
# #             response = self.middleware(request)
# #             self.assertEqual(response.status_code, 302)
# #             self.assertRedirects(response, reverse("onboarding:step1"))

# # def test_no_redirection_when_onboarded(self):
# #     # Test that no redirection occurs when user is onboarded
# #     self.profile.is_onboarded = True
# #     self.profile.save()

# #     request = self.factory.get("/some-view/")
# #     request.user = self.user

# #     response = self.middleware(request)
# #     self.assertEqual(
# #         response.status_code, 200
# #     )  # No redirection, so status code should be 200

# # def test_no_redirection_for_admin_logout_onboarding_routes(self):
# #     # Test that no redirection occurs for admin, logout, or onboarding routes
# #     self.profile.is_onboarded = False
# #     self.profile.save()

# #     # Test admin route
# #     request = self.factory.get(reverse("admin:index"))
# #     request.user = self.user
# #     response = self.middleware(request)
# #     self.assertEqual(response.status_code, 200)  # Should pass through middleware

# #     # Test logout route
# #     request = self.factory.get(reverse("logout"))
# #     request.user = self.user
# #     response = self.middleware(request)
# #     self.assertEqual(response.status_code, 200)  # Should pass through middleware

# #     # Test onboarding route
# #     request = self.factory.get(reverse("onboarding:step1"))
# #     request.user = self.user
# #     response = self.middleware(request)
# #     self.assertEqual(response.status_code, 200)  # Should pass through middleware
