from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.tests.factories import GroupFactory, GroupMemberFactory
from kns.onboarding.models import ProfileCompletionTask
from kns.skills.models import ProfileInterest, ProfileSkill, Skill


class TestGroupFactory(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_factory(self):
        """
        The factory produces a valid instance of Group.
        """
        group = GroupFactory()

        self.assertIsNotNone(group)
        self.assertNotEqual(group.name, "")
        self.assertNotEqual(group.description, "")
        self.assertIsNotNone(group.leader)
        self.assertIsNotNone(group.location_country)
        self.assertIsNotNone(group.location_city)

    def test_str_method(self):
        """
        Return the correct string representation of the group.
        """
        group = GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
        )

        self.assertEqual(
            str(group),
            "Bible Study Group - Nigeria (Lagos)",
        )


class TestGroupMemberFactory(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        User.objects.create_user(
            email="adminuser@example.com",
            password="oldpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_factory(self):
        """
        The factory produces a valid instance of GroupMember.
        """
        group_member = GroupMemberFactory()

        self.assertIsNotNone(group_member)
        self.assertIsNotNone(group_member.profile)
        self.assertIsNotNone(group_member.group)

    def test_str_method(self):
        """
        The __str__ method returns the correct string representation of the group member.
        """
        group = GroupFactory()

        group_member = GroupMemberFactory(
            profile=self.profile,
            group=group,
        )

        self.assertEqual(
            str(group_member),
            f"{self.profile.get_full_name()} ({group.name})",
        )


class TestGroupMethods(TestCase):
    def setUp(self):
        self.client = Client()

        # Create unique users
        self.user1 = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )

        # Create profiles for the users
        self.profile1 = self.user1.profile
        self.profile1.date_of_birth = date.today() - timedelta(
            days=365 * 30,
        )
        self.profile1.save()

        self.group = GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
            leader=self.profile1,
        )

        self.user2 = User.objects.create_user(
            email="member2@example.com",
            password="password",
        )
        self.profile2 = self.user2.profile
        self.profile2.date_of_birth = date.today() - timedelta(
            days=365 * 25,
        )
        self.profile2.save()

        self.user3 = User.objects.create_user(
            email="member3@example.com",
            password="password",
        )
        self.profile3 = self.user3.profile
        self.profile3.date_of_birth = date.today() - timedelta(
            days=365 * 35,
        )
        self.profile3.save()

        self.user4 = User.objects.create_user(
            email="member4@example.com",
            password="password",
        )
        self.profile4 = self.user4.profile

        # Create group members with unique profiles
        self.member1 = GroupMemberFactory(
            profile=self.profile1,
            group=self.group,
        )
        self.member2 = GroupMemberFactory(
            profile=self.profile2,
            group=self.group,
        )
        self.member3 = GroupMemberFactory(
            profile=self.profile3,
            group=self.group,
        )

        # Create two descendant groups, one in the same city, one in a different city
        self.child_group_same_city = GroupFactory(
            parent=self.group,
            leader=self.profile2,
            name="Child Group Lagos",
            location_country="Nigeria",
            location_city="Lagos",
        )

        self.child_group_different_city = GroupFactory(
            parent=self.group,
            leader=self.profile3,
            name="Child Group Abuja",
            location_country="Nigeria",
            location_city="Abuja",
        )

        # Create a grandchild group in the same city
        self.grandchild_group_same_city = GroupFactory(
            parent=self.child_group_same_city,
            leader=self.profile4,
            name="Grandchild Group Lagos",
            location_country="Nigeria",
            location_city="Lagos",
        )

        skill = Skill.objects.create(
            title="Leadership",
            content="Leadership skill",
            author=self.profile1,
        )

        skill2 = Skill.objects.create(
            title="Communication",
            content="Communication skill",
            author=self.profile1,
        )

        ProfileSkill.objects.create(
            profile=self.profile3,
            skill=skill,
        )

        ProfileSkill.objects.create(
            profile=self.profile3,
            skill=skill2,
        )

        ProfileInterest.objects.create(
            profile=self.profile3,
            interest=skill,
        )

        ProfileInterest.objects.create(
            profile=self.profile3,
            interest=skill2,
        )

    def test_group_members(self):
        members = self.group.group_members()
        self.assertIn(self.profile1, members)
        self.assertIn(self.profile2, members)
        self.assertIn(self.profile3, members)

    def test_add_member(self):
        new_user = User.objects.create_user(
            email="member5@example.com",
            password="password",
        )

        new_profile = new_user.profile
        self.group.add_member(new_profile)

        group_members = self.group.group_members()
        self.assertIn(new_profile, group_members)

    def test_leaders_count(self):
        self.assertEqual(
            self.group.leaders_count(),
            0,
        )

        self.profile1.role = "leader"
        self.profile1.save()

        self.assertEqual(
            self.group.leaders_count(),
            1,
        )

    def test_total_members_count(self):
        self.assertEqual(
            self.group.total_members_count(),
            4,
        )

    def test_members_count(self):
        self.assertEqual(
            self.group.members_count(),
            3,
        )

    def test_external_persons_count(self):
        self.assertEqual(
            self.group.external_persons_count(),
            0,
        )

        self.profile3.role = "external_person"
        self.profile3.save()

        self.assertEqual(
            self.group.external_persons_count(),
            1,
        )

    def test_male_count(self):
        self.assertEqual(
            self.group.male_count(),
            3,
        )

    def test_female_count(self):
        self.assertEqual(
            self.group.female_count(),
            0,
        )

        self.profile1.gender = "female"
        self.profile2.gender = "female"

        self.profile1.save()
        self.profile2.save()

        self.assertEqual(
            self.group.female_count(),
            2,
        )

    def test_mentors_count(self):
        self.assertEqual(
            self.group.mentors_count(),
            0,
        )

        self.profile1.is_mentor = True
        self.profile1.save()

        self.assertEqual(
            self.group.mentors_count(),
            1,
        )

    def test_skill_trainers_count(self):
        self.profile1.is_skill_training_facilitator = True
        self.profile1.save()

        self.assertEqual(
            self.group.skill_trainers_count(),
            1,
        )

    def test_movement_trainers_count(self):
        self.profile1.is_movement_training_facilitator = True
        self.profile1.save()
        self.assertEqual(
            self.group.movement_trainers_count(),
            1,
        )

    def test_most_common_role(self):
        self.assertEqual(
            self.group.most_common_role(),
            "member",
        )

    def test_get_absolute_url(self):
        expected_url = reverse(
            "groups:group_overview",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

        self.assertEqual(
            self.group.get_absolute_url(),
            expected_url,
        )

    def test_get_activities_url(self):
        expected_url = reverse(
            "groups:group_activities",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

        self.assertEqual(
            self.group.get_activities_url(),
            expected_url,
        )

    def test_get_members_url(self):
        expected_url = reverse(
            "groups:group_members",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

        self.assertEqual(
            self.group.get_members_url(),
            expected_url,
        )

    def test_get_subgroups_url(self):
        expected_url = reverse(
            "groups:group_subgroups",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

        self.assertEqual(
            self.group.get_subgroups_url(),
            expected_url,
        )

    def test_location_display_with_country_and_city(self):
        """
        Test the location_display method with both country and city.
        """

        self.assertEqual(
            self.group.location_display(),
            ", Lagos",
        )

    def test_location_display_with_country_only(self):
        """
        Test the location_display method when only country is provided.
        """
        self.group.location_city = ""
        self.group.save()

        self.assertEqual(
            self.group.location_display(),
            "",
        )

    def test_location_display_with_no_location(self):
        """
        Test the location_display method when no location is provided.
        """
        self.group.location_city = ""
        self.group.location_country = None
        self.group.save()

        self.assertEqual(
            self.group.location_display(),
            "None",
        )

    def test_is_member(self):
        """
        Test if the is_member method correctly identifies members.
        """
        self.assertTrue(self.group.is_member(self.profile1))
        self.assertTrue(self.group.is_member(self.profile2))

    def test_add_member_existing(self):
        """
        Test adding an existing member to the group.
        """
        self.group.add_member(self.profile1)
        self.assertEqual(self.group.members.count(), 3)

    def test_add_member_new(self):
        """
        Test adding a new member to the group.
        """
        new_user = User.objects.create_user(
            email="newmember@example.com",
            password="password",
        )
        new_profile = new_user.profile

        self.group.add_member(new_profile)
        self.assertEqual(self.group.members.count(), 4)
        self.assertTrue(self.group.is_member(new_profile))

    def test_get_close_city_groups_same_city(self):
        """
        Test that get_close_city_groups returns only descendants
        that are in the same city as the group.
        """
        local_groups = self.group.get_close_city_groups()

        # Ensure only the groups in the same city are returned
        self.assertIn(self.child_group_same_city, local_groups)
        self.assertIn(self.grandchild_group_same_city, local_groups)
        self.assertNotIn(self.child_group_different_city, local_groups)

    def test_get_close_city_groups_exclude_self(self):
        """
        Test that the method excludes the group itself from the result.
        """
        local_groups = self.group.get_close_city_groups()

        # Ensure the parent group itself is excluded
        self.assertNotIn(self.group, local_groups)

    def test_get_close_city_groups_different_city(self):
        """
        Test that get_close_city_groups doesn't return groups
        in a different city.
        """
        local_groups = self.group.get_close_city_groups()

        # Ensure the group in a different city is not returned
        self.assertNotIn(self.child_group_different_city, local_groups)

    def test_get_close_city_groups_called_on_child(self):
        """
        Test that get_close_city_groups works correctly when called
        on a child group, ensuring that the parent's descendants are returned.
        """
        # Call the method on a child group that has a parent
        local_groups = self.child_group_same_city.get_close_city_groups()

        # Ensure that descendants of the parent group are returned
        self.assertIn(self.grandchild_group_same_city, local_groups)
        self.assertNotIn(self.child_group_different_city, local_groups)

        # Ensure that the group itself (child_group_same_city) is excluded
        self.assertNotIn(self.child_group_same_city, local_groups)

        # Test for the average_age method

    def test_get_close_country_groups_same_country(self):
        """
        Test that get_close_country_groups returns only descendants
        that are in the same country as the group.
        """
        national_groups = self.group.get_close_country_groups()

        # Ensure the groups in the same country are returned
        self.assertIn(self.child_group_same_city, national_groups)
        self.assertIn(self.grandchild_group_same_city, national_groups)
        self.assertIn(self.child_group_different_city, national_groups)

    def test_get_close_country_groups_exclude_self(self):
        """
        Test that the method excludes the group itself from the result.
        """
        national_groups = self.group.get_close_country_groups()

        # Ensure the parent group itself is excluded
        self.assertNotIn(self.group, national_groups)

    def test_get_close_country_groups_called_on_child(self):
        """
        Test that get_close_country_groups works correctly when called
        on a child group, ensuring that the parent's descendants are returned.
        """
        # Call the method on a child group that has a parent
        national_groups = self.child_group_same_city.get_close_country_groups()

        # Ensure that descendants of the parent group are returned
        self.assertIn(self.grandchild_group_same_city, national_groups)
        self.assertIn(self.child_group_different_city, national_groups)

        # Ensure that the group itself (child_group_same_city) is excluded
        self.assertNotIn(self.child_group_same_city, national_groups)

    def test_get_close_country_groups_different_country(self):
        """
        Test that get_close_country_groups doesn't return groups
        in a different country (assuming we add a group in a different country).
        """
        # Create a new group in a different country
        user9 = User.objects.create_user(
            email="member9@example.com",
            password="password",
        )
        profile9 = user9.profile
        profile9.date_of_birth = date.today() - timedelta(
            days=365 * 25,
        )
        profile9.save()

        self.child_group_different_country = GroupFactory(
            parent=self.group,
            leader=profile9,
            name="Child Group USA",
            location_country="US",
            location_city="New York",
        )

        national_groups = self.group.get_close_country_groups()

        # Ensure the group in a different country is not returned
        self.assertNotIn(
            self.child_group_different_country,
            national_groups,
        )

    def test_average_age(self):
        # Get the actual ages of the members
        actual_ages = [member.profile.get_age() for member in self.group.members.all()]

        # Expected average age calculation based on printed values
        expected_average_age = sum(actual_ages) / len(actual_ages)

        # Assert the calculated average matches the expected average
        self.assertAlmostEqual(
            self.group.average_age(),
            expected_average_age,
        )

    def test_average_age_with_no_birthdate(self):
        # Set one profile without a birthdate
        self.profile3.date_of_birth = None
        self.profile3.save()

        # Print the ages of the remaining profiles
        print(f"Profile1 age: {self.profile1.get_age()}")
        print(f"Profile2 age: {self.profile2.get_age()}")

        # Only profile1 (30) and profile2 (25) should be counted
        expected_average_age = (29 + 24) / 2

        self.assertAlmostEqual(
            self.group.average_age(),
            expected_average_age,
        )

    def test_average_age_with_no_members_with_birthdate(self):
        # Set all profiles without a birthdate
        self.profile1.date_of_birth = None
        self.profile1.save()

        self.profile2.date_of_birth = None
        self.profile2.save()

        self.profile3.date_of_birth = None
        self.profile3.save()

        # Should return None since no members have a birthdate
        self.assertEqual(self.group.average_age(), "---")

    def test_unique_skills(self):
        # Test that unique_skills returns the correct unique skills
        unique_skills = self.group.unique_skills()
        expected_skills = [
            "Leadership",
            "Communication",
        ]

        # Check if the expected skills are in the queryset
        for skill in expected_skills:
            self.assertIn(
                skill,
                unique_skills,
            )

        # Ensure there are no duplicates
        self.assertEqual(
            unique_skills.count(),
            len(
                set(expected_skills),
            ),
        )

    def test_unique_interests(self):
        # Test that unique_interests returns the correct unique interests
        unique_interests = self.group.unique_interests()
        expected_interests = [
            "Leadership",
            "Communication",
        ]

        # Check if the expected interests are in the queryset
        for interest in expected_interests:
            self.assertIn(
                interest,
                unique_interests,
            )

        # Ensure there are no duplicates
        self.assertEqual(
            unique_interests.count(),
            len(
                set(expected_interests),
            ),
        )

    def test_sister_groups(self):
        """
        Test that sister_groups returns only groups with the same parent.
        """
        # Create an additional sibling group (another sister group)
        another_user = User.objects.create_user(
            email="another_user4@example.com",
            password="password",
        )

        another_sister_group = GroupFactory(
            parent=self.group.parent,
            name="Another Sister Group",
            location_country="Nigeria",
            location_city="Ibadan",
            leader=another_user.profile,
        )

        # Get the sister groups
        sister_groups = another_sister_group.sister_groups()

        # Ensure that only the sibling groups are returned
        self.assertEqual(sister_groups.count(), 1)

    def test_child_groups(self):
        """
        Test that child_groups returns only the direct child groups of the group.
        """
        # Get the child groups of the main group
        child_groups = self.group.child_groups()

        # Ensure that only the direct child groups are returned
        self.assertIn(self.child_group_same_city, child_groups)
        self.assertIn(self.child_group_different_city, child_groups)
        self.assertNotIn(
            self.grandchild_group_same_city, child_groups
        )  # Ensure grandchildren aren't included
        self.assertNotIn(
            self.group, child_groups
        )  # Ensure the group itself is excluded

    def test_child_groups_on_child(self):
        """
        Test child_groups method on a child group to ensure it returns its own child groups.
        """
        # Call child_groups on a child group
        child_groups_of_child = self.child_group_same_city.child_groups()

        # Ensure that the grandchild group is returned
        self.assertIn(self.grandchild_group_same_city, child_groups_of_child)
        self.assertNotIn(
            self.group, child_groups_of_child
        )  # Ensure parent group is not included

    def test_remove_member(self):
        """
        Test the remove_member method to ensure a member is correctly removed from the group
        and that it returns the correct value.
        """
        self.group.add_member(self.profile1)

        # Ensure profile1 is a member of the group
        self.assertTrue(self.group.is_member(self.profile1))

        # Remove the member from the group
        removed = self.group.remove_member(self.profile1)

        # Check that the member has been removed and the method returns True
        self.assertTrue(removed)
        self.assertNotIn(self.profile1, self.group.group_members())

        non_user = User.objects.create_user(
            email="non_user@example.com",
            password="password",
        )

        non_member_profile = non_user.profile
        removed_non_member = self.group.remove_member(non_member_profile)

        # Check that the method returns False since the profile was not a member
        self.assertFalse(removed_non_member)


class TestGroupSignals(TestCase):
    def setUp(self):
        # Create user and profile
        self.user1 = User.objects.create_user(
            email="leader@example.com",
            password="password",
        )
        self.profile1 = self.user1.profile

        self.profile1.role = "leader"
        self.profile1.save()

        self.profile1.create_profile_completion_tasks()

    def test_mark_register_group_complete_task_exists(self):
        """
        Test if the 'register_group' task is marked complete when a group is created.
        """
        # Create a group with user1 as the leader
        GroupFactory(
            leader=self.profile1,
            name="Youth Fellowship Group",
        )

        register_group_task = ProfileCompletionTask.objects.get(
            profile=self.profile1, task_name="register_group"
        )

        # Refresh the task from the database
        register_group_task.refresh_from_db()

        # Assert that the task is marked as complete
        self.assertTrue(register_group_task.is_complete)

    def test_mark_register_group_complete_no_task(self):
        """
        Test that nothing happens if no 'register_group' task exists for the user.
        """
        # Create another user and profile without a 'register_group' task
        user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )

        profile2 = user2.profile

        # Create a group with user2 as the leader
        GroupFactory(
            leader=profile2,
            name="New Members Group",
        )

        # Assert that no tasks exist for profile2
        self.assertFalse(
            ProfileCompletionTask.objects.filter(
                profile=profile2,
                task_name="register_group",
            ).exists()
        )

    def test_mark_register_group_complete_task_already_complete(self):
        """
        Test that if the 'register_group' task is already complete, it remains complete.
        """
        self.register_group_task = ProfileCompletionTask.objects.get(
            profile=self.profile1,
            task_name="register_group",
        )

        # Mark the task as already complete
        self.register_group_task.is_complete = True
        self.register_group_task.save()

        # Create a group with user1 as the leader
        GroupFactory(
            leader=self.profile1,
            name="Youth Leadership Group",
        )

        # Refresh the task from the database
        self.register_group_task.refresh_from_db()

        # Assert that the task is still complete
        self.assertTrue(self.register_group_task.is_complete)

    def test_mark_register_group_complete_signal_not_fired(self):
        """
        Test that the signal is not fired when an existing group is updated.
        """
        # Create a group with user1 as the leader
        group = GroupFactory(
            leader=self.profile1,
            name="Bible Study Group",
        )

        self.register_group_task = ProfileCompletionTask.objects.get(
            profile=self.profile1,
            task_name="register_group",
        )

        # Refresh the task to confirm it's marked complete
        self.register_group_task.refresh_from_db()
        self.assertTrue(self.register_group_task.is_complete)

        # Reset task completion to False and update the existing group
        self.register_group_task.is_complete = False
        self.register_group_task.save()

        group.name = "Updated Bible Study Group"
        group.save()

        # Assert that the task is still not marked as complete
        self.register_group_task.refresh_from_db()
        self.assertFalse(self.register_group_task.is_complete)


class TestGroupMemberSignals(TestCase):
    def setUp(self):
        # Create user and profile
        self.user1 = User.objects.create_user(
            email="leader@example.com",
            password="password",
        )
        self.profile1 = self.user1.profile

        self.profile1.role = "leader"
        self.profile1.save()

        self.profile1.create_profile_completion_tasks()

        # Create a group with profile1 as the leader
        self.group = GroupFactory(
            leader=self.profile1,
            name="Fellowship Group",
        )

    def test_mark_register_first_member_complete_task_exists(self):
        """
        Test if the 'register_first_member' task is marked complete
        when the first group member is added.
        """
        # Add the first member to the group
        GroupMemberFactory(
            profile=self.profile1,
            group=self.group,
        )

        # Fetch the 'register_first_member' task
        register_first_member_task = ProfileCompletionTask.objects.get(
            profile=self.profile1, task_name="register_first_member"
        )

        # Refresh from the database and assert it's complete
        register_first_member_task.refresh_from_db()
        self.assertTrue(register_first_member_task.is_complete)

    def test_mark_register_first_member_complete_no_task(self):
        """
        Test that nothing happens if no 'register_first_member' task exists for the user.
        """
        # Create another user and profile without a 'register_first_member' task
        user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        profile2 = user2.profile

        # Create a group with profile2 as the leader
        group2 = GroupFactory(
            leader=profile2,
            name="Second Group",
        )

        # Add the first member to the new group
        GroupMemberFactory(
            profile=profile2,
            group=group2,
        )

        # Assert no 'register_first_member' task exists for profile2
        self.assertFalse(
            ProfileCompletionTask.objects.filter(
                profile=profile2,
                task_name="register_first_member",
            ).exists()
        )

    def test_mark_register_first_member_complete_task_already_complete(self):
        """
        Test that if the 'register_first_member' task is already complete, it remains complete.
        """
        # Fetch and mark the 'register_first_member' task as complete
        register_first_member_task = ProfileCompletionTask.objects.get(
            profile=self.profile1, task_name="register_first_member"
        )
        register_first_member_task.is_complete = True
        register_first_member_task.save()

        # Add the first member to the group
        GroupMemberFactory(
            profile=self.profile1,
            group=self.group,
        )

        # Refresh from the database and assert it's still complete
        register_first_member_task.refresh_from_db()
        self.assertTrue(register_first_member_task.is_complete)

    def test_mark_register_first_member_signal_not_fired_for_existing_member(self):
        """
        Test that the signal is not fired when an existing group member is updated.
        """
        # Add the first member to the group
        member = GroupMemberFactory(
            profile=self.profile1,
            group=self.group,
        )

        # Fetch and mark the task as complete
        register_first_member_task = ProfileCompletionTask.objects.get(
            profile=self.profile1, task_name="register_first_member"
        )
        register_first_member_task.is_complete = True
        register_first_member_task.save()

        # Update the existing group member
        member.role = "new role"
        member.save()

        # Refresh and ensure task is still complete
        register_first_member_task.refresh_from_db()
        self.assertTrue(register_first_member_task.is_complete)
