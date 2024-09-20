from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import test_constants

from ..models import MakeLeaderActionApproval, Setting
from .factories import FAQFactory


class TestFAQ(TestCase):
    def test_factory(self):
        """
        The factory produces a valid instance.
        """
        faq = FAQFactory()

        self.assertIsNotNone(faq)
        self.assertNotEqual(faq.question, "")
        self.assertNotEqual(faq.answer, "")

    def test_str_method(self):
        """
        The __str__ method returns the question of the FAQ.
        """
        faq = FAQFactory(question="What is KNS?")

        self.assertEqual(str(faq), "What is KNS?")


class TestSetting(TestCase):
    def setUp(self):
        """
        Set up the test environment by ensuring no existing `Setting` instance
        before each test case.
        """
        Setting.objects.all().delete()
        self.setting = Setting.get_or_create_setting()

    def test_clean_method(self):
        """
        Test the clean method to ensure that minimum mentorship duration
        does not exceed maximum mentorship duration.
        """
        setting = Setting(
            min_mentorship_duration_weeks=10, max_mentorship_duration_weeks=5
        )
        with self.assertRaises(ValidationError):
            setting.clean()

    def test_save_method(self):
        """
        Test the save method to ensure only one instance of Setting
        exists.
        """
        # This should not create a new instance
        new_setting = Setting()
        new_setting.save()

        self.assertEqual(Setting.objects.count(), 1)
        self.assertEqual(self.setting.pk, new_setting.pk)

    def test_get_or_create_setting(self):
        """
        Test the get_or_create_setting method to ensure it returns an instance
        of Setting, creating one if it does not exist.
        """
        setting = Setting.get_or_create_setting()

        self.assertIsInstance(setting, Setting)
        self.assertEqual(Setting.objects.count(), 1)

        new_setting = Setting.get_or_create_setting()

        self.assertEqual(setting.pk, new_setting.pk)

    def test_str_method(self):
        """
        Test __str__ method of the model.
        """
        setting = Setting.get_or_create_setting()
        self.assertEqual(str(setting), "Settings")


class TestMakeLeaderActionApproval(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a default MakeLeaderActionApproval instance.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        self.group_leader_user = User.objects.create_user(
            email="group_leader@example.com",
            password="password",
        )
        self.group_leader_profile = self.group_leader_user.profile

        # Create a group
        self.group = Group.objects.create(
            leader=self.group_leader_profile,
            name="Test Group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        # Create another profile to act as the new leader
        self.leader_user = User.objects.create_user(
            email="leaderuser@example.com",
            password="password",
        )
        self.leader_profile = self.leader_user.profile

        self.group.add_member(self.leader_profile)

        # Create a MakeLeaderActionApproval instance
        self.action_approval = MakeLeaderActionApproval.objects.create(
            created_by=self.profile,
            group_created_for=self.group,
            new_leader=self.leader_profile,
            action_type="change_role_to_leader",
        )

    def test_str_method(self):
        """
        Test the string representation of the MakeLeaderActionApproval model.
        """
        expected_str = f"Change role to leader ({self.leader_profile.get_full_name()})"

        self.assertEqual(str(self.action_approval), expected_str)

    def test_check_timeout(self):
        """
        Test the check_timeout method to ensure it updates the status to 'expired'
        when the approval has timed out.
        """
        # Simulate a timeout by setting created_at to past time
        self.action_approval.created_at = timezone.now() - timedelta(days=8)
        self.action_approval.check_timeout()
        self.assertEqual(self.action_approval.status, "expired")

    def test_action_type_display(self):
        """
        Test the action_type_display method to ensure it returns the correct
        human-readable string.
        """
        self.assertEqual(
            self.action_approval.action_type_display(),
            "Change role to leader",
        )

    def test_approve_method_not_consumer(self):
        """
        Test the approve method to ensure the action is not approved if the
        consumer is not the person designated to approve the action.
        """
        approver_user = User.objects.create_user(
            email="approver@example.com",
            password="password",
        )
        approver_profile = approver_user.profile

        self.action_approval.approve(approver_profile)
        self.assertEqual(self.action_approval.status, "pending")

    def test_approve_method_is_consumer(self):
        """
        Test the approve method to ensure the action is correctly approved
        and the new leader's role is updated.
        """
        self.action_approval.approve(self.group_leader_profile)
        self.assertEqual(self.action_approval.status, "approved")
        self.assertEqual(self.action_approval.approved_by, self.group_leader_profile)
        self.assertEqual(self.action_approval.new_leader.role, "leader")
        self.assertIsNotNone(self.action_approval.approved_at)

    def test_reject_method_not_consumer(self):
        """
        Test the reject method to ensure the action is not modified if
        profile is not designated consumer.
        """
        # Create another profile to act as the new leader
        approver_user = User.objects.create_user(
            email="approveruser@example.com",
            password="password",
        )
        approver_profile = approver_user.profile

        self.action_approval.reject(approver_profile)
        self.assertEqual(self.action_approval.status, "pending")

    def test_reject_method_is_consumer(self):
        """
        Test the reject method to ensure the action is correctly rejected.
        """
        self.action_approval.reject(self.group_leader_profile)

        self.assertEqual(self.action_approval.status, "rejected")
        self.assertIsNone(self.action_approval.approved_by)
        self.assertIsNone(self.action_approval.approved_at)

    def test_notification_display(self):
        """
        Test the notification_display method to ensure it returns the correct message.
        """
        expected_message = (
            f"{self.profile.get_full_name()} requests to promote "
            f"{self.leader_profile.get_full_name()} from a member to a "
            "leader role."
        )

        self.assertEqual(
            self.action_approval.notification_display(),
            expected_message,
        )
