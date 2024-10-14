from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.utils import timezone

from kns.custom_user.models import User

from ..models import Setting
from .factories import FAQFactory, NotificationFactory, NotificationRecipientFactory


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


class TestNotification(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        self.client = Client()

        # Create users and their profiles
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
        )
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        # Create notification instances
        self.notification = NotificationFactory(sender=self.profile)

    def test_factory(self):
        """
        The factory produces a valid instance.
        """
        notification = NotificationFactory()

        self.assertIsNotNone(notification)
        self.assertNotEqual(notification.notification_type, "")
        self.assertNotEqual(notification.message, "")

    def test_str_method(self):
        """
        The __str__ method returns a formatted string for the Notification.
        """
        notification = NotificationFactory(notification_type="Group Move")
        expected_str = (
            "Notification [Group Move] - "
            f"{notification.created_at.strftime('%Y-%m-%d')}"
        )

        self.assertEqual(str(notification), expected_str)

    def test_add_recipient(self):
        """
        Test the `add_recipient` method to ensure recipients can be added.
        """
        notification = NotificationFactory()
        recipient = self.profile  # Use manually created profile

        notification.add_recipient(recipient=recipient)

        self.assertEqual(notification.recipients.count(), 1)
        self.assertEqual(notification.recipients.first().recipient, recipient)

    def test_mark_as_read_for_user(self):
        """
        Test the `mark_as_read_for_user` method to ensure a notification is marked
        as read for a specific user.
        """
        notification = NotificationFactory()
        recipient = self.profile  # Use manually created profile
        notification.add_recipient(recipient=recipient)

        recipient_record = notification.recipients.first()
        self.assertFalse(recipient_record.is_read)

        notification.mark_as_read_for_user(user=recipient)

        recipient_record.refresh_from_db()
        self.assertTrue(recipient_record.is_read)


class TestNotificationRecipient(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        self.client = Client()

        # Create users and their profiles
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
        )
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        # Create a notification and notification recipient
        self.notification = NotificationFactory(sender=self.profile)
        self.recipient = self.profile  # Use manually created profile

    def test_factory(self):
        """
        The factory produces a valid instance of NotificationRecipient.
        """
        # Create a notification recipient using the factory
        notification_recipient = NotificationRecipientFactory()

        # Assertions to verify the object was created properly
        self.assertIsNotNone(notification_recipient)
        self.assertEqual(
            notification_recipient.recipient, self.recipient
        )  # The recipient should match the manually created profile
        self.assertFalse(notification_recipient.is_read)  # Default should be unread
        self.assertIsNone(
            notification_recipient.read_at
        )  # read_at should be None if not read

    def test_str_method(self):
        """
        The __str__ method returns a formatted string for the NotificationRecipient.
        """
        notification_recipient = NotificationRecipientFactory(
            notification=self.notification,
            recipient=self.recipient,
            is_read=False,
        )
        expected_str = (
            f"Notification '{notification_recipient.notification.notification_type}' "
            f"for {self.recipient} - Unread"
        )

        self.assertEqual(str(notification_recipient), expected_str)

    def test_mark_as_read(self):
        """
        Test the `mark_as_read` method to ensure the notification is marked as read.
        """
        notification_recipient = NotificationRecipientFactory(is_read=False)

        self.assertFalse(notification_recipient.is_read)
        self.assertIsNone(notification_recipient.read_at)

        notification_recipient.mark_as_read()

        notification_recipient.refresh_from_db()
        self.assertTrue(notification_recipient.is_read)
        self.assertIsNotNone(notification_recipient.read_at)
        self.assertAlmostEqual(
            notification_recipient.read_at,
            timezone.now(),
            delta=timezone.timedelta(seconds=1),
        )
