import pytest

from ..forms import GroupForm
from . import test_constants


@pytest.fixture
def form_data():
    """
    Fixture for GroupForm data.
    """
    return {
        "name": "Test Group",
        "location_country": "US",
        "description": test_constants.VALID_GROUP_DESCRIPTION,
        "location_city": "New York",
        "image": None,
    }


def test_group_form_valid(form_data):
    form = GroupForm(data=form_data)

    assert form.is_valid()


def test_group_name_too_long(form_data):
    form_data["name"] = "A" * 51  # Exceeds the 50 character limit
    form = GroupForm(data=form_data)

    assert not form.is_valid()
    assert "name" in form.errors


def test_group_description_missing(form_data):
    form_data["description"] = ""
    form = GroupForm(data=form_data)

    assert not form.is_valid()
    assert "description" in form.errors


def test_group_invalid_country_code(form_data):
    form_data["location_country"] = "ZZ"  # Invalid country code
    form = GroupForm(data=form_data)

    assert not form.is_valid()
    assert "location_country" in form.errors


def test_group_city_missing(form_data):
    form_data["location_city"] = ""
    form = GroupForm(data=form_data)

    assert not form.is_valid()
    assert "location_city" in form.errors
