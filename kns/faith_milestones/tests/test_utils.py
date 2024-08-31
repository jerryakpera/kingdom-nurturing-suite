from django.test import TestCase

from kns.custom_user.models import User
from kns.faith_milestones.db_data import milestones as milestones_data
from kns.faith_milestones.models import FaithMilestone
from kns.faith_milestones.utils import populate_faith_milestones


class PopulateFaithMilestonesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.milestones_data = milestones_data

    def test_populate_faith_milestones_with_empty_data(self):
        """
        Test that no milestones are created when the input list is empty.
        """
        populate_faith_milestones([])
        milestones_count = FaithMilestone.objects.count()

        self.assertEqual(milestones_count, 0)

    def test_populate_faith_milestones_with_valid_data(self):
        """
        Test that faith milestones are created when valid data is provided.
        """
        populate_faith_milestones(self.milestones_data)
        milestones_count = FaithMilestone.objects.count()

        self.assertEqual(
            milestones_count,
            len(self.milestones_data),
        )

        for milestone_data in self.milestones_data:
            self.assertTrue(
                FaithMilestone.objects.filter(
                    title=milestone_data["title"],
                ).exists()
            )

    def test_populate_faith_milestones_with_duplicate_data(self):
        """
        Test that no duplicate milestones are created.
        """
        populate_faith_milestones(self.milestones_data)

        # Attempt to populate the same data again
        populate_faith_milestones(self.milestones_data)

        # The number of milestones should not have increased
        milestones_count = FaithMilestone.objects.count()
        self.assertEqual(
            milestones_count,
            len(self.milestones_data),
        )

    def test_populate_faith_milestones_assigns_author(self):
        """Test that the first profile is assigned as the author."""
        populate_faith_milestones(self.milestones_data)

        for milestone in FaithMilestone.objects.all():
            self.assertEqual(
                milestone.author,
                self.profile,
            )
