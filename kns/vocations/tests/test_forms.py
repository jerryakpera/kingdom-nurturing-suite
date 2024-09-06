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

        self.vocation1 = Vocation.objects.create(
            title="Teacher",
            description="Builds and maintains software systems.",
            author=self.profile,
        )
        self.vocation2 = Vocation.objects.create(
            title="Engineer",
            description="Builds and maintains software systems.",
            author=self.profile,
        )
        self.vocation3 = Vocation.objects.create(
            title="Doctor",
            description="Builds and maintains software systems.",
            author=self.profile,
        )

    def test_profile_vocation_form_initial(self):
        """
        Test the initial state of the ProfileVocationForm.
        """
        form = ProfileVocationForm()

        # Ensure that the field is required
        self.assertTrue(form.fields["vocation"].required)

        # Check that all vocations are included in the queryset
        self.assertQuerySetEqual(
            form.fields["vocation"].queryset.order_by("title"),
            Vocation.objects.all().order_by("title"),
            transform=lambda x: x,
        )

    def test_profile_vocation_form_valid_data(self):
        """
        Test the ProfileVocationForm with valid data.
        """
        form_data = {
            "vocation": self.vocation2.id,
        }
        form = ProfileVocationForm(data=form_data)

        self.assertTrue(form.is_valid())

        # Save the form and check the selected vocation
        vocation_instance = form.cleaned_data.get("vocation")
        self.assertEqual(vocation_instance.title, "Engineer")

    def test_profile_vocation_form_invalid_data(self):
        """
        Test the ProfileVocationForm with invalid data (empty selection).
        """
        form_data = {
            "vocation": "",  # No vocation selected
        }
        form = ProfileVocationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("vocation", form.errors)

    def test_profile_vocation_form_missing_required_field(self):
        """
        Test the ProfileVocationForm with a missing required field.
        """
        form_data = {}  # No data provided for the vocation field
        form = ProfileVocationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("vocation", form.errors)

    def test_profile_vocation_form_valid_data_on_instance(self):
        """
        Test the ProfileVocationForm with valid data on an instance of ProfileVocation.
        """
        form_data = {
            "vocation": self.vocation3.id,  # Select the "Doctor" vocation
        }
        form = ProfileVocationForm(data=form_data)

        self.assertTrue(form.is_valid())
        vocation_instance = form.cleaned_data.get("vocation")
        self.assertEqual(vocation_instance.title, "Doctor")
