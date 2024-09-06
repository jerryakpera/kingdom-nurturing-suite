from django.test import Client, TestCase

from kns.custom_user.models import User
from kns.vocations.forms import ProfileVocationForm
from kns.vocations.models import ProfileVocation, Vocation


class TestProfileVocationForm(TestCase):
    def setUp(self):
        """
        Set up a few sample vocations for testing.
        """
        self.client = Client()

        # Create a user and a profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        # Create sample vocations
        self.vocation1 = Vocation.objects.create(
            title="Teacher",
            description="Educates students.",
            author=self.profile,
        )
        self.vocation2 = Vocation.objects.create(
            title="Engineer",
            description="Builds and maintains systems.",
            author=self.profile,
        )
        self.vocation3 = Vocation.objects.create(
            title="Doctor",
            description="Provides medical care.",
            author=self.profile,
        )

    def test_profile_vocation_form_initial(self):
        """
        Test the initial state of the ProfileVocationForm.
        """
        form = ProfileVocationForm()

        # Ensure that the field is required
        self.assertTrue(form.fields["vocations"].required)

        # Check that all vocations are included in the queryset
        self.assertQuerySetEqual(
            form.fields["vocations"].queryset.order_by("title"),
            Vocation.objects.all().order_by("title"),
            transform=lambda x: x,
        )

    def test_profile_vocation_form_valid_data(self):
        """
        Test the ProfileVocationForm with valid data.
        """
        form_data = {
            "vocations": [self.vocation2.id, self.vocation3.id],
        }
        form = ProfileVocationForm(data=form_data)

        self.assertTrue(form.is_valid())

        # Save the form and check the selected vocations
        vocation_instances = form.cleaned_data.get("vocations")
        self.assertEqual(len(vocation_instances), 2)
        self.assertIn(self.vocation2, vocation_instances)
        self.assertIn(self.vocation3, vocation_instances)

    def test_profile_vocation_form_invalid_data(self):
        """
        Test the ProfileVocationForm with invalid data (empty selection).
        """
        form_data = {
            "vocations": [],  # No vocations selected
        }
        form = ProfileVocationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("vocations", form.errors)

    def test_profile_vocation_form_missing_required_field(self):
        """
        Test the ProfileVocationForm with a missing required field.
        """
        form_data = {}  # No data provided for the vocations field
        form = ProfileVocationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("vocations", form.errors)

    def test_profile_vocation_form_valid_data_on_instance(self):
        """
        Test the ProfileVocationForm with valid data on an instance of ProfileVocation.
        """
        form_data = {
            "vocations": [
                self.vocation1.id,
                self.vocation3.id,
            ],  # Select "Teacher" and "Doctor"
        }
        form = ProfileVocationForm(data=form_data)

        self.assertTrue(form.is_valid())
        vocation_instances = form.cleaned_data.get("vocations")
        self.assertEqual(len(vocation_instances), 2)
        self.assertIn(self.vocation1, vocation_instances)
        self.assertIn(self.vocation3, vocation_instances)
