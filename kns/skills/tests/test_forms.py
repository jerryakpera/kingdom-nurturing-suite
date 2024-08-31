from django.test import TestCase

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.skills.forms import ProfileSkillsForm
from kns.skills.models import Skill


class TestProfileSkillsForm(TestCase):
    def setUp(self):
        """
        Create a user, mock settings, and create some skills.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.settings = Setting.get_or_create_setting()

        self.settings.max_skills_per_user = 3
        self.settings.max_interests_per_user = 2

        self.settings.save()

        self.skill1 = Skill.objects.create(
            title="Skill 1",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill2 = Skill.objects.create(
            title="Skill 2",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill3 = Skill.objects.create(
            title="Skill 3",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill4 = Skill.objects.create(
            title="Skill 4",
            content="This is test content for a skill",
            author=self.profile,
        )

    def test_valid_form(self):
        """
        Test that the form is valid when selecting a valid number of skills and interests.
        """
        form_data = {
            "skills": [self.skill1.id, self.skill2.id],
            "interests": [self.skill3.id],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with valid data",
        )

    def test_invalid_form_with_too_many_skills(self):
        """
        Test that the form is invalid when selecting more skills than allowed.
        """
        form_data = {
            "skills": [self.skill1.id, self.skill2.id, self.skill3.id, self.skill4.id],
            "interests": [self.skill1.id],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertFalse(
            form.is_valid(),
            "Form should be invalid with too many skills",
        )

        self.assertIn(
            "skills",
            form.errors,
        )

        self.assertEqual(
            form.errors["skills"][0],
            f"You can select up to {self.settings.max_skills_per_user} skills.",
        )

    def test_invalid_form_with_too_many_interests(self):
        """
        Test that the form is invalid when selecting more interests than allowed.
        """
        form_data = {
            "skills": [self.skill1.id],
            "interests": [
                self.skill2.id,
                self.skill3.id,
                self.skill4.id,
            ],
        }
        form = ProfileSkillsForm(data=form_data)

        self.assertFalse(
            form.is_valid(),
            "Form should be invalid with too many interests",
        )
        self.assertIn(
            "interests",
            form.errors,
        )

        self.assertEqual(
            form.errors["interests"][0],
            f"You can select up to {self.settings.max_interests_per_user} interests.",
        )

    def test_valid_form_with_empty_skills_and_interests(self):
        """
        Test that the form is valid when no skills or interests are selected.
        """
        form_data = {
            "skills": [],
            "interests": [],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with no skills or interests selected",
        )
