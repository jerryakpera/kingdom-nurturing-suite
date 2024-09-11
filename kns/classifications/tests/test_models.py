import pytest
from django.db import IntegrityError
from django.test import TestCase

from kns.classifications.models import (
    Classification,
    ClassificationSubclassification,
    ProfileClassification,
    Subclassification,
)
from kns.custom_user.models import User


class TestClassificationModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

    def test_classification_creation(self):
        """
        Test that a Classification instance can be created and is properly saved.
        """
        classification = Classification.objects.create(
            title="Science",
            content="<p>Scientific classifications</p>",
            order=1,
            author=self.profile,
        )

        self.assertEqual(classification.title, "Science")
        self.assertEqual(classification.content, "<p>Scientific classifications</p>")
        self.assertEqual(classification.order, 1)

    def test_classification_slug_unique(self):
        """
        Test that the slug field on the Classification model is unique.
        """
        Classification.objects.create(
            title="Science",
            content="<p>Scientific classifications</p>",
            order=1,
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Classification.objects.create(
                title="Science",
                content="<p>Different content</p>",
                order=2,
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_classification_str_method(self):
        """
        Test that the __str__ method returns the title of the classification.
        """
        classification = Classification.objects.create(
            title="Science",
            content="<p>Scientific classifications</p>",
            order=1,
            author=self.profile,
        )

        assert str(classification) == "Science"


class TestSubclassificationModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

    def test_subclassification_creation(self):
        """
        Test that a Subclassification instance can be created and is properly saved.
        """
        subclassification = Subclassification.objects.create(
            title="Biology",
            content="<p>Biological subclassifications</p>",
            author=self.profile,
        )

        self.assertEqual(subclassification.title, "Biology")
        self.assertEqual(
            subclassification.content, "<p>Biological subclassifications</p>"
        )

    def test_subclassification_slug_unique(self):
        """
        Test that the slug field on the Subclassification model is unique.
        """
        Subclassification.objects.create(
            title="Biology",
            content="<p>Biological subclassifications</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Subclassification.objects.create(
                title="Biology",
                content="<p>Different content</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_subclassification_str_method(self):
        """
        Test that the __str__ method returns the title of the subclassification.
        """
        subclassification = Subclassification.objects.create(
            title="Biology",
            content="<p>Biological subclassifications</p>",
            author=self.profile,
        )

        assert str(subclassification) == "Biology"


class TestClassificationSubclassificationModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Classification and Subclassification instance.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.classification = Classification.objects.create(
            title="Science",
            content="<p>Scientific classifications</p>",
            order=1,
            author=self.profile,
        )

        self.subclassification = Subclassification.objects.create(
            title="Biology",
            content="<p>Biological subclassifications</p>",
            author=self.profile,
        )

    def test_classification_subclassification_creation(self):
        """
        Test that a ClassificationSubclassification instance can be created.
        """
        classification_subclassification = (
            ClassificationSubclassification.objects.create(
                classification=self.classification,
                subclassification=self.subclassification,
            )
        )

        self.assertEqual(str(classification_subclassification), "Science (Biology)")

    def test_classification_subclassification_unique_constraint(self):
        """
        Test that the ClassificationSubclassification unique constraint works.
        """
        ClassificationSubclassification.objects.create(
            classification=self.classification,
            subclassification=self.subclassification,
        )

        with pytest.raises(IntegrityError):
            ClassificationSubclassification.objects.create(
                classification=self.classification,
                subclassification=self.subclassification,
            )


class TestProfileClassificationModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile, Classification, and Subclassification instance.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.classification = Classification.objects.create(
            title="Science",
            content="<p>Scientific classifications</p>",
            order=1,
            author=self.profile,
        )

        self.subclassification = Subclassification.objects.create(
            title="Biology",
            content="<p>Biological subclassifications</p>",
            author=self.profile,
        )

    def test_profile_classification_creation(self):
        """
        Test that a ProfileClassification instance can be created with a classification.
        """
        profile_classification = ProfileClassification.objects.create(
            no=1,
            profile=self.profile,
            classification=self.classification,
        )

        self.assertEqual(
            str(profile_classification),
            "Test User - Science",
        )

    def test_profile_classification_with_subclassification(self):
        """
        Test that a ProfileClassification instance can be created with
        a classification and subclassification.
        """
        profile_classification = ProfileClassification.objects.create(
            no=2,
            profile=self.profile,
            classification=self.classification,
            subclassification=self.subclassification,
        )

        self.assertEqual(
            str(profile_classification),
            "Test User - Science (Biology)",
        )
