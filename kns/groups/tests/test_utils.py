from django.test import TestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.utils import GroupStatistics


class TestGroupStatistics(TestCase):
    def setUp(self):
        # Create users and profiles
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        # Create groups with varying number of members, cities, and countries
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group 1",
            location_country="NG",
            location_city="Lagos",
            description="Test group 1",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group 2",
            location_country="NG",
            location_city="Abuja",
            description="Test group 2",
        )
        self.group3 = Group.objects.create(
            leader=self.profile3,
            name="Group 3",
            location_country="KE",
            location_city="Nairobi",
            description="Test group 3",
        )

        # Add members to the groups
        self.group1.add_member(profile=self.profile2)
        self.group1.add_member(profile=self.profile3)

        self.statistics = GroupStatistics(Group.objects.all())

    def test_get_no_groups(self):
        """
        Test the get_no_groups method to ensure it returns the correct
        number of groups.
        """
        self.assertEqual(self.statistics.get_no_groups(), 3)

    def test_get_top_3_cities_with_most_groups(self):
        """
        Test the get_top_3_cities_with_most_groups method to ensure it
        returns the correct cities.
        """
        result = self.statistics.get_top_3_cities_with_most_groups()

        expected = [
            {
                "location_city": "Lagos",
                "group_count": 1,
            },
            {
                "location_city": "Abuja",
                "group_count": 1,
            },
            {
                "location_city": "Nairobi",
                "group_count": 1,
            },
        ]

        # Sort both results by city name for comparison
        result = sorted(result, key=lambda x: x["location_city"])
        expected = sorted(expected, key=lambda x: x["location_city"])

        self.assertQuerySetEqual(result, expected, transform=lambda x: x)

    def test_get_top_3_countries_with_most_groups(self):
        """
        Test the get_top_3_countries_with_most_groups method to ensure it
        returns the correct countries.
        """
        result = self.statistics.get_top_3_countries_with_most_groups()
        expected = [
            {"location_country": "NG", "group_count": 2},
            {"location_country": "KE", "group_count": 1},
        ]
        # Fix the method name to assertQuerySetEqual
        self.assertQuerySetEqual(result, expected, transform=lambda x: x)

    def test_get_most_recent_group(self):
        """
        Test the get_most_recent_group method to ensure it returns the
        correct group.
        """
        self.user4 = User.objects.create_user(
            email="user4@example.com",
            password="password",
        )
        self.profile4 = self.user4.profile
        self.group4 = Group.objects.create(
            leader=self.profile4,
            name="Group 4",
            location_country="KE",
            location_city="Nairobi",
            description="Test group 4",
        )

        self.assertEqual(
            self.statistics.get_most_recent_group(),
            self.group4,
        )

    def test_get_group_with_most_members(self):
        """
        Test the get_group_with_most_members method to ensure it returns
        the group with the most members.
        """
        self.assertEqual(
            self.statistics.get_group_with_most_members(),
            self.group1,
        )

    def test_get_avg_no_of_members_per_group(self):
        """
        Test the get_avg_no_of_members_per_group method to ensure it
        calculates the correct average.
        """
        avg_members = (2 + 0 + 0) / 3
        self.assertEqual(
            self.statistics.get_avg_no_of_members_per_group(),
            round(avg_members, 1),
        )

    def test_get_all_statistics(self):
        """
        Test the get_all_statistics method to ensure it returns the
        correct statistics.
        """
        stats = self.statistics.get_all_statistics()

        # Check each statistic
        self.assertEqual(stats[0]["value"], 3)

        # Expectation adjusted based on members excluding leaders (2 + 0 + 0)
        self.assertEqual(
            stats[1]["value"], f"{(2 + 0 + 0) / 3:.1f}"
        )  # This will be 0.7
        self.assertIn("Nigeria (2)", stats[2]["value"])
        self.assertIn("Lagos", stats[3]["value"])
        # self.assertEqual(stats[4]["value"], self.group3)
