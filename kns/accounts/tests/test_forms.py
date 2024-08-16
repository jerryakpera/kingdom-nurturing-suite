import pytest

from kns.custom_user.models import User

from ..forms import ChangePasswordForm, LoginForm, SetPasswordForm


@pytest.fixture
def user():
    """
    Fixture to create a test user.
    """
    return User.objects.create_user(
        email="testuser@example.com",
        password="oldpassword",
    )


@pytest.fixture
def form_data():
    """
    Fixture for form data.
    """
    return {
        "current_password": "oldpassword",
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123",
    }


def test_change_password_form_valid(form_data):
    form = ChangePasswordForm(data=form_data)

    assert form.is_valid()


def test_new_password_similar_to_current(form_data):
    form_data["new_password"] = "oldpassword"

    form = ChangePasswordForm(data=form_data)

    assert not form.is_valid()
    assert "new_password" in form.errors


def test_change_passwords_do_not_match(form_data):
    form_data["confirm_new_password"] = "mismatch"
    form = ChangePasswordForm(data=form_data)

    assert not form.is_valid()
    assert "confirm_new_password" in form.errors


def test_login_form_valid(user):
    form_data = {
        "email": "testuser@example.com",
        "password": "password123",
    }

    form = LoginForm(data=form_data)

    assert form.is_valid()


def test_invalid_email():
    form_data = {
        "email": "invalidemail",
        "password": "password123",
    }
    form = LoginForm(data=form_data)

    assert not form.is_valid()
    assert "email" in form.errors


def test_set_password_form_valid():
    form_data = {
        "new_password": "newpassword123",
        "confirm_password": "newpassword123",
    }

    form = SetPasswordForm(data=form_data)

    assert form.is_valid()


def test_password_too_short():
    form_data = {
        "new_password": "short",
        "confirm_password": "short",
    }

    form = SetPasswordForm(data=form_data)

    assert not form.is_valid()
    assert "new_password" in form.errors


def test_set_passwords_do_not_match():
    form_data = {
        "new_password": "newpassword123",
        "confirm_password": "mismatch",
    }

    form = SetPasswordForm(data=form_data)

    assert not form.is_valid()
    assert "confirm_password" in form.errors
