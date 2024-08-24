from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Setting
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
