from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from kns.custom_user.models import User
from kns.discipleships.models import Discipleship
from kns.profiles.models import Profile  # Assuming you have a Profile model


class TestDiscipleshipMethods(TestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.profile2 = self.user2.profile
        self.profile2.first_name = "Jane"
        self.profile2.last_name = "Pritchet"
        self.profile2.save()

        # Create a discipleship instance
        self.discipleship = Discipleship.objects.create(
            disciple=self.profile,
            discipler=self.profile2,
            author=self.profile,
            group="group_member",
        )

    def test_str_representation(self):
        expected_str = (
            f"{self.discipleship.group} discipleship of "
            f"{self.profile} by {self.profile2}"
        )
        self.assertEqual(str(self.discipleship), expected_str)

    def test_group_display(self):
        self.assertEqual(
            self.discipleship.group_display(),
            "Group member",
        )

    def test_running_time_less_than_a_week(self):
        self.assertEqual(
            self.discipleship.running_time(),
            "less than a week",
        )

    def test_running_time_one_month(self):
        # Set created_at to one month ago
        self.discipleship.created_at = timezone.now() - timedelta(days=30)
        self.discipleship.save()
        self.assertEqual(
            self.discipleship.running_time(),
            "1 month",
        )

    def test_running_time_one_month_and_two_weeks(self):
        # Set created_at to 6 weeks ago
        self.discipleship.created_at = timezone.now() - timedelta(days=42)
        self.discipleship.save()
        self.assertEqual(
            self.discipleship.running_time(),
            "1 month and 1 week",
        )

    def test_total_running_time_no_sent_forth(self):
        # Set created_at to two months ago
        self.discipleship.created_at = timezone.now() - timedelta(days=60)
        self.discipleship.save()
        self.assertEqual(
            self.discipleship.total_running_time(),
            "2 months",
        )

    def test_total_running_time_with_sent_forth(self):
        # Create a sent_forth discipleship
        Discipleship.objects.create(
            disciple=self.profile,
            discipler=self.profile2,
            author=self.profile,
            group="sent_forth",
            created_at=timezone.now() - timedelta(days=10),
        )

        # Check total running time considering sent_forth
        self.assertEqual(
            self.discipleship.total_running_time(),
            "less than a week",
        )

    def test_total_running_time_with_completed_at(self):
        # Set completed_at to one month ago
        self.discipleship.completed_at = timezone.now() - timedelta(days=30)
        self.discipleship.save()
        self.assertEqual(
            self.discipleship.total_running_time(),
            "-1 month",
        )

    def test_total_running_time_one_week(self):
        # Set created_at to 1 week ago
        self.discipleship.created_at = timezone.now() - timedelta(weeks=1)
        self.discipleship.save()
        self.assertEqual(
            self.discipleship.total_running_time(),
            "1 week",
        )
