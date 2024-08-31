from django.test import TestCase

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.faith_milestones.forms import ProfileFaithMilestonesForm
from kns.faith_milestones.models import FaithMilestone


class TestProfileFaithMilestonesForm(TestCase):
    def setUp(self):
        """
        Create a user, mock settings, and create some faith milestones.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.settings = Setting.get_or_create_setting()

        self.settings.save()

        self.faith_milestone1 = FaithMilestone.objects.create(
            title="Faith milestone 1",
            description="This is test description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone2 = FaithMilestone.objects.create(
            title="Faith milestone 2",
            description="This is test description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone3 = FaithMilestone.objects.create(
            title="Faith milestone 3",
            description="This is test description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone4 = FaithMilestone.objects.create(
            title="Faith milestone 4",
            description="This is test description for a faith milestone",
            author=self.profile,
        )

    def test_valid_form(self):
        """
        Test that the form is valid when selecting a valid number of
        faith milestones and interests.
        """
        form_data = {
            "faith_milestones": [
                self.faith_milestone1.id,
                self.faith_milestone2.id,
            ],
        }

        form = ProfileFaithMilestonesForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with valid data",
        )

    def test_valid_form_with_empty_faith_milestones(self):
        """
        Test that the form is valid when no faith milestones are selected.
        """
        form_data = {
            "faith_milestones": [],
        }

        form = ProfileFaithMilestonesForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with no faith milestones.",
        )
