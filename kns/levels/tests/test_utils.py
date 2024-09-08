from django.test import TestCase

from kns.custom_user.models import User

from ..db_data import levels as predefined_levels
from ..db_data import sublevels as predefined_sublevels
from ..models import Level, Sublevel
from ..utils import populate_levels, populate_sublevels


class PopulateLevelsAndSublevelsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data by creating a user and profile.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        # Define some predefined levels and sublevels for testing
        self.predefined_levels = predefined_levels
        self.predefined_sublevels = predefined_sublevels

    def test_levels_are_created_correctly(self):
        """
        Test that levels are created correctly based on predefined data.
        """
        populate_levels(self.predefined_levels)

        # Check that the correct number of levels were created
        self.assertEqual(
            Level.objects.count(),
            len(
                self.predefined_levels,
            ),
        )

        # Check that each level was created with the correct data
        for level_data in self.predefined_levels:
            level = Level.objects.get(title=level_data["title"])

            self.assertEqual(level.content, level_data["content"])
            self.assertEqual(level.author, self.profile)

    def test_sublevels_are_created_correctly(self):
        """
        Test that sublevels are created correctly based on predefined data.
        """
        populate_sublevels(self.predefined_sublevels)

        # Check that the correct number of sublevels were created
        self.assertEqual(
            Sublevel.objects.count(),
            len(
                self.predefined_sublevels,
            ),
        )

        # Check that each sublevel was created with the correct data
        for sublevel_data in self.predefined_sublevels:
            sublevel = Sublevel.objects.get(
                title=sublevel_data["title"],
            )
            self.assertEqual(
                sublevel.content,
                sublevel_data["content"],
            )
            self.assertEqual(sublevel.author, self.profile)

    def test_no_levels_created_if_no_predefined_levels(self):
        """
        Test that no levels are created if the predefined levels list is empty.
        """
        populate_levels([])

        # Check that no levels were created
        self.assertEqual(Level.objects.count(), 0)

    def test_no_sublevels_created_if_no_predefined_sublevels(self):
        """
        Test that no sublevels are created if the predefined sublevels list is empty.
        """
        populate_sublevels([])

        # Check that no sublevels were created
        self.assertEqual(Sublevel.objects.count(), 0)

    def test_level_is_not_created_if_exists(self):
        """
        Test that no duplicate levels are created if a level with the same title already exists.
        """
        # Create an initial level
        Level.objects.create(
            title="Beginner Level",
            content="Introduction to basic concepts.",
            author=self.profile,
        )

        # Call the function with a level that already exists
        populate_levels(self.predefined_levels)

        # Check that only one level with the title "Beginner Level" exists
        self.assertEqual(
            Level.objects.filter(
                title="Beginner Level",
            ).count(),
            1,
        )

    def test_sublevel_is_not_created_if_exists(self):
        """
        Test that no duplicate sublevels are created if a sublevel with
        the same title already exists.
        """
        # Create an initial sublevel
        Sublevel.objects.create(
            title="Basic Concepts",
            content="Fundamentals of the subject.",
            author=self.profile,
        )

        # Call the function with a sublevel that already exists
        populate_sublevels(self.predefined_sublevels)

        # Check that only one sublevel with the title "Basic Concepts" exists
        self.assertEqual(
            Sublevel.objects.filter(
                title="Basic Concepts",
            ).count(),
            1,
        )

    def test_first_profile_is_set_as_author_for_levels(self):
        """
        Test that the first profile in the database is set as the author
        for all created levels.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_levels(self.predefined_levels)

        # Check that the first profile is used as the author for all levels
        for level in Level.objects.all():
            self.assertEqual(level.author, self.profile)

    def test_first_profile_is_set_as_author_for_sublevels(self):
        """
        Test that the first profile in the database is set as the author for all created sublevels.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="anotheruser@example.com",
            password="password",
        )

        # Call the function
        populate_sublevels(self.predefined_sublevels)

        # Check that the first profile is used as the author for all sublevels
        for sublevel in Sublevel.objects.all():
            self.assertEqual(sublevel.author, self.profile)
