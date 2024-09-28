import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from kns.custom_user.models import User
from kns.skills.models import ProfileInterest, ProfileSkill, Skill


class TestSkillModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """

        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_skill_creation(self):
        """
        Test that a Skill instance can be created and is properly saved.
        """
        skill = Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

        self.assertEqual(skill.title, "Python Programming")
        self.assertEqual(
            skill.content,
            "<p>Advanced Python programming skills.</p>",
        )

    def test_skill_slug_unique(self):
        """
        Test that the slug field on the Skill model is unique.
        """
        Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            Skill.objects.create(
                title="Python Programming",
                content="<p>Different content.</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_skill_str_method(self):
        """
        Test that the __str__ method returns the title of the skill.
        """
        skill = Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

        assert str(skill) == "Python Programming"


class TestProfileSkillModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile and Skill instances linked to the test user.
        """

        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.profile.first_name = "John"
        self.profile.last_name = "Doe"

        self.profile.save()

        self.skill = Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

    def test_profile_skill_creation(self):
        """
        Test that a ProfileSkill instance can be created and is properly saved.
        """
        profile_skill = ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )

        assert profile_skill.profile == self.profile
        assert profile_skill.skill == self.skill

    def test_profile_skill_unique_together(self):
        """
        Test that the combination of profile and skill is unique in ProfileSkill.
        """
        ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileSkill.objects.create(
                profile=self.profile,
                skill=self.skill,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_profile_skill_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        profile_skill = ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )

        self.assertEqual(str(profile_skill), "John Doe - Python Programming")

    def test_profile_skill_clean(self):
        """
        Test that a ProfileSkill instance raises ValidationError if the skill
        is also listed as an interest.
        """
        ProfileInterest.objects.create(
            profile=self.profile,
            interest=self.skill,
        )

        profile_skill = ProfileSkill(
            profile=self.profile,
            skill=self.skill,
        )

        with pytest.raises(ValidationError) as excinfo:
            profile_skill.clean()

        self.assertTrue(
            "The skill 'Python Programming' is already listed as an interest for this profile."
            in str(excinfo.value)
        )


class TestProfileInterestModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile and Skill instances linked to the test user.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.profile.first_name = "John"
        self.profile.last_name = "Doe"

        self.profile.save()

        self.skill = Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

    def test_profile_interest_creation(self):
        """
        Test that a ProfileInterest instance can be created and is properly saved.
        """
        profile_interest = ProfileInterest.objects.create(
            profile=self.profile, interest=self.skill
        )

        self.assertEqual(
            profile_interest.profile,
            self.profile,
        )
        self.assertEqual(
            profile_interest.interest,
            self.skill,
        )

    def test_profile_interest_unique_together(self):
        """
        Test that the combination of profile and interest is unique in ProfileInterest.
        """
        ProfileInterest.objects.create(
            profile=self.profile,
            interest=self.skill,
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileInterest.objects.create(
                profile=self.profile,
                interest=self.skill,
            )

        self.assertTrue(
            "UNIQUE constraint failed" in str(excinfo.value),
        )

    def test_profile_interest_clean(self):
        """
        Test that a ProfileInterest instance raises ValidationError
        if the interest is also listed as a skill.
        """
        ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )

        profile_interest = ProfileInterest(
            profile=self.profile,
            interest=self.skill,
        )

        with pytest.raises(ValidationError) as excinfo:
            profile_interest.clean()

        self.assertTrue(
            "The interest 'Python Programming' is already listed as a skill for this profile."
            in str(excinfo.value)
        )

    def test_profile_interest_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        profile_interest = ProfileInterest.objects.create(
            profile=self.profile,
            interest=self.skill,
        )

        self.assertEqual(
            str(profile_interest),
            "John Doe - Python Programming",
        )
