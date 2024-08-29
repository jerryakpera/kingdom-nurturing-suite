from django.test import TestCase

from kns.custom_user.models import User

from ..models import Skill
from ..skills_data import skills as predefined_skills
from ..utils import populate_skills


class PopulateSkillsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        # Modify predefined_skills for testing if necessary
        self.predefined_skills = predefined_skills

    def test_skills_are_created_correctly(self):
        # Override the skills in the module with test data

        # Call the function
        populate_skills(self.predefined_skills)

        # Check that the correct number of skills were created
        self.assertEqual(Skill.objects.count(), len(self.predefined_skills))

        # Check that each skill was created with the correct data
        for i, skill_data in enumerate(self.predefined_skills):
            skill = Skill.objects.get(title=skill_data["title"])
            self.assertEqual(skill.content, skill_data["content"])
            self.assertEqual(skill.author, self.profile)

    def test_no_skills_created_if_no_predefined_skills(self):
        # Override the skills in the module with an empty list
        self.predefined_skills = []

        # Call the function
        populate_skills(self.predefined_skills)

        # Check that no skills were created
        self.assertEqual(Skill.objects.count(), 0)

    def test_first_profile_is_set_as_author(self):
        # Ensure there is more than one profile in the database
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_skills(self.predefined_skills)

        # Check that the first profile is set as the author for all skills
        for skill in Skill.objects.all():
            self.assertEqual(skill.author, self.profile)
