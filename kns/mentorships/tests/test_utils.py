from django.test import TestCase

from kns.custom_user.models import User
from kns.mentorships.models import MentorshipArea, MentorshipGoal
from kns.mentorships.utils import populate_mentorship_areas, populate_mentorship_goals
from kns.profiles.models import Profile


class PopulateMentorshipAreasTestCase(TestCase):
    def setUp(self):
        """
        Set up test data by creating a user and profile.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        # Define some predefined mentorship areas for testing
        self.predefined_mentorship_areas = [
            {
                "title": "Software Development",
                "content": "Learn to code.",
            },
            {
                "title": "Data Science",
                "content": "Learn data analysis.",
            },
        ]

    def test_mentorship_areas_are_created_correctly(self):
        """
        Test that mentorship areas are created correctly based on predefined data.
        """
        populate_mentorship_areas(self.predefined_mentorship_areas)

        # Check that the correct number of mentorship areas were created
        self.assertEqual(
            MentorshipArea.objects.count(),
            len(self.predefined_mentorship_areas),
        )

        # Check that each mentorship area was created with the correct data
        for mentorship_area_data in self.predefined_mentorship_areas:
            mentorship_area = MentorshipArea.objects.get(
                title=mentorship_area_data["title"]
            )

            self.assertEqual(
                mentorship_area.content,
                mentorship_area_data["content"],
            )

            self.assertEqual(mentorship_area.author, self.profile)

    def test_no_mentorship_areas_created_if_no_predefined_mentorship_areas(self):
        """
        Test that no mentorship areas are created if the predefined
        mentorship areas list is empty.
        """
        populate_mentorship_areas([])

        # Check that no mentorship areas were created
        self.assertEqual(MentorshipArea.objects.count(), 0)

    def test_mentorship_area_is_not_created_if_exists(self):
        """
        Test that no duplicate mentorship areas are created if an area
        with the same title already exists.
        """
        # Create an initial mentorship area
        MentorshipArea.objects.create(
            title="Software Development",
            content="Learn to code.",
            author=self.profile,
        )

        # Call the function with a mentorship area that already exists
        populate_mentorship_areas(self.predefined_mentorship_areas)

        # Check that only one mentorship area with the title "Software Development" exists
        self.assertEqual(
            MentorshipArea.objects.filter(
                title="Software Development",
            ).count(),
            1,
        )

    def test_first_profile_is_set_as_author_for_mentorship_areas(self):
        """
        Test that the first profile in the database is set as the author
        for all created mentorship areas.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_mentorship_areas(self.predefined_mentorship_areas)

        # Check that the first profile is used as the author for all mentorship areas
        for mentorship_area in MentorshipArea.objects.all():
            self.assertEqual(mentorship_area.author, self.profile)


class PopulateMentorshipGoalsTestCase(TestCase):
    def setUp(self):
        """
        Set up test data by creating a user and profile.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        # Define some predefined mentorship goals for testing
        self.predefined_mentorship_goals = [
            {
                "title": "Learn Python",
                "content": "Master Python programming.",
            },
            {
                "title": "Learn Data Analysis",
                "content": "Analyze data with Python.",
            },
        ]

    def test_mentorship_goals_are_created_correctly(self):
        """
        Test that mentorship goals are created correctly based on predefined data.
        """
        populate_mentorship_goals(self.predefined_mentorship_goals)

        # Check that the correct number of mentorship goals were created
        self.assertEqual(
            MentorshipGoal.objects.count(),
            len(self.predefined_mentorship_goals),
        )

        # Check that each mentorship goal was created with the correct data
        for mentorship_goal_data in self.predefined_mentorship_goals:
            mentorship_goal = MentorshipGoal.objects.get(
                title=mentorship_goal_data["title"]
            )
            self.assertEqual(
                mentorship_goal.content,
                mentorship_goal_data["content"],
            )
            self.assertEqual(
                mentorship_goal.author,
                self.profile,
            )

    def test_no_mentorship_goals_created_if_no_predefined_mentorship_goals(self):
        """
        Test that no mentorship goals are created if the predefined
        mentorship goals list is empty.
        """
        populate_mentorship_goals([])

        # Check that no mentorship goals were created
        self.assertEqual(MentorshipGoal.objects.count(), 0)

    def test_mentorship_goal_is_not_created_if_exists(self):
        """
        Test that no duplicate mentorship goals are created if a goal
        with the same title already exists.
        """
        # Create an initial mentorship goal
        MentorshipGoal.objects.create(
            title="Learn Python",
            content="Master Python programming.",
            author=self.profile,
        )

        # Call the function with a mentorship goal that already exists
        populate_mentorship_goals(self.predefined_mentorship_goals)

        # Check that only one mentorship goal with the title "Learn Python" exists
        self.assertEqual(
            MentorshipGoal.objects.filter(
                title="Learn Python",
            ).count(),
            1,
        )

    def test_first_profile_is_set_as_author_for_mentorship_goals(self):
        """
        Test that the first profile in the database is set as the author
        for all created mentorship goals.
        """
        # Create another profile to ensure there is more than one profile in the database
        User.objects.create_user(
            email="anotheruser@example.com",
            password="password",
        )

        # Call the function
        populate_mentorship_goals(self.predefined_mentorship_goals)

        # Check that the first profile is used as the author for all mentorship goals
        for mentorship_goal in MentorshipGoal.objects.all():
            self.assertEqual(mentorship_goal.author, self.profile)
