from django.test import TestCase

from ..models import FAQ
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
