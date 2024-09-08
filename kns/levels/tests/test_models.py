import pytest
from django.db import IntegrityError
from django.test import TestCase

from kns.custom_user.models import User
from kns.levels.models import Level, LevelSublevel, ProfileLevel, Sublevel
from kns.profiles.models import Profile


class TestLevelModel(TestCase):
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

    def test_level_creation(self):
        """
        Test that a Level instance can be created and is properly saved.
        """
        level = Level.objects.create(
            title="Advanced Leadership",
            content="<p>Leadership strategies and techniques.</p>",
            author=self.profile,
        )

        self.assertEqual(level.title, "Advanced Leadership")
        self.assertEqual(level.content, "<p>Leadership strategies and techniques.</p>")

    def test_level_slug_unique(self):
        """
        Test that the slug field on the Level model is unique.
        """
        Level.objects.create(
            title="Advanced Leadership",
            content="<p>Leadership strategies and techniques.</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Level.objects.create(
                title="Advanced Leadership",
                content="<p>Different content.</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_level_str_method(self):
        """
        Test that the __str__ method returns the title of the level.
        """
        level = Level.objects.create(
            title="Advanced Leadership",
            content="<p>Leadership strategies and techniques.</p>",
            author=self.profile,
        )

        assert str(level) == "Advanced Leadership"


class TestSublevelModel(TestCase):
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

    def test_sublevel_creation(self):
        """
        Test that a Sublevel instance can be created and is properly saved.
        """
        sublevel = Sublevel.objects.create(
            title="Team Management",
            content="<p>Managing teams effectively.</p>",
            author=self.profile,
        )

        self.assertEqual(sublevel.title, "Team Management")
        self.assertEqual(sublevel.content, "<p>Managing teams effectively.</p>")

    def test_sublevel_slug_unique(self):
        """
        Test that the slug field on the Sublevel model is unique.
        """
        Sublevel.objects.create(
            title="Team Management",
            content="<p>Managing teams effectively.</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Sublevel.objects.create(
                title="Team Management",
                content="<p>Different content.</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_sublevel_str_method(self):
        """
        Test that the __str__ method returns the title of the sublevel.
        """
        sublevel = Sublevel.objects.create(
            title="Team Management",
            content="<p>Managing teams effectively.</p>",
            author=self.profile,
        )

        assert str(sublevel) == "Team Management"


class TestLevelSublevelModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Level and Sublevel instance.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.level = Level.objects.create(
            title="Advanced Leadership",
            content="<p>Leadership strategies and techniques.</p>",
            author=self.profile,
        )

        self.sublevel = Sublevel.objects.create(
            title="Team Management",
            content="<p>Managing teams effectively.</p>",
            author=self.profile,
        )

    def test_level_sublevel_creation(self):
        """
        Test that a LevelSublevel instance can be created.
        """
        level_sublevel = LevelSublevel.objects.create(
            level=self.level,
            sublevel=self.sublevel,
        )

        self.assertEqual(str(level_sublevel), "Advanced Leadership (Team Management)")

    def test_level_sublevel_unique_constraint(self):
        """
        Test that the LevelSublevel unique constraint works.
        """
        LevelSublevel.objects.create(
            level=self.level,
            sublevel=self.sublevel,
        )

        with pytest.raises(IntegrityError):
            LevelSublevel.objects.create(
                level=self.level,
                sublevel=self.sublevel,
            )


class TestProfileLevelModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile, Level, and Sublevel instance.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.level = Level.objects.create(
            title="Advanced Leadership",
            content="<p>Leadership strategies and techniques.</p>",
            author=self.profile,
        )

        self.sublevel = Sublevel.objects.create(
            title="Team Management",
            content="<p>Managing teams effectively.</p>",
            author=self.profile,
        )

    def test_profile_level_creation(self):
        """
        Test that a ProfileLevel instance can be created with a level.
        """
        profile_level = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level,
        )

        self.assertEqual(str(profile_level), "Test User - Advanced Leadership")

    def test_profile_level_with_sublevel(self):
        """
        Test that a ProfileLevel instance can be created with a level and sublevel.
        """
        profile_level = ProfileLevel.objects.create(
            profile=self.profile,
            level=self.level,
            sublevel=self.sublevel,
        )

        self.assertEqual(
            str(profile_level), "Test User - Advanced Leadership (Team Management)"
        )
