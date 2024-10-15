import pytest
from rest_framework import status
from unittest.mock import patch

from api.services.avatar import Avatar
from users.models import RegistrationToken, User

BASE_URL = "/api/register/"


@pytest.mark.django_db
def test_avatar_logic(user):
    avatar = Avatar()

    with patch.object(Avatar, "get_random_avatar", return_value=b"Image"):
        avatar.set_avatar(user)

    assert User.objects.first().avatar is not None


@pytest.mark.django_db
@patch("users.tasks.send_confirmation_email")
@patch("users.tasks.get_and_set_random_avatar.delay")
def test_create_user(mock_delay_email, mock_random_avatar, client):
    """Test case to create a new user."""

    count_before = User.objects.count()

    response = client().post(
        path=BASE_URL,
        data={
            "first_name": "Test",
            "last_name": "Test",
            "email": "test_email@email.ru",
            "username": "Test",
            "password": "PASSWORD",
            "phone_number": "123456789",
            "call_availability": "Any time",
        },
    )

    assert User.objects.count() == count_before + 1
    assert User.objects.last().avatar is not None
    assert response.status_code == status.HTTP_201_CREATED
    mock_random_avatar.assert_called_once()
    mock_delay_email.delay.assert_called_once()


@pytest.mark.django_db
def test_confirmation_email(client, token):
    """Test case to confirm a new user."""

    count_before = RegistrationToken.objects.count()
    token = RegistrationToken.objects.first().token

    response = client().get(f"{BASE_URL}confirm/{token}")

    assert RegistrationToken.objects.count() == count_before - 1
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_auth_token(client, user, auth_token):
    """Test case to get an auth token."""

    data = {"password": "PASSWORD", "email": user.email}
    response = client().post(path="/api/auth/token/login/", data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auth_token"] == auth_token
