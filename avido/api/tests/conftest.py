import pytest
from rest_framework.test import APIClient

from advertisement.enums import AdvertisementStatus, ModerationDecision
from advertisement.models import (
    Advertisement,
    AdvertisementCategory,
    City,
    ModerationRecordHistory,
    Region,
)
from users.db_utils import create_token
from users.enums import UsersRole, UsersStatus
from users.models import RegistrationToken, User


@pytest.fixture
def client():
    return APIClient


@pytest.fixture
def user(client) -> User:
    client().post(
        path="/api/register/",
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

    user = User.objects.first()
    user.is_active = True
    user.status = UsersStatus.ACTIVE.value
    user.save()

    return user


@pytest.fixture
def token(user) -> RegistrationToken:
    return create_token(user)


@pytest.fixture
def region() -> Region:
    return Region.objects.create(name="Region")


@pytest.fixture
def city(region) -> City:
    return City.objects.create(name="City", region=region)


@pytest.fixture
def category() -> AdvertisementCategory:
    future_parent_category = AdvertisementCategory.objects.create(
        name="Category 1",
        slug="category-1",
        description="description",
        sort_order=1,
        parent_category=None,
    )

    return AdvertisementCategory.objects.create(
        name="Category 2",
        slug="category-2",
        description="description",
        sort_order=2,
        parent_category=future_parent_category,
    )


@pytest.fixture
def auth_token(client, user):
    data = {"password": "PASSWORD", "email": user.email}
    response = client().post(path="/api/auth/token/login/", data=data)

    return response.json().get("auth_token")


@pytest.fixture
def admin(client) -> User:
    client().post(
        path="/api/register/",
        data={
            "first_name": "Test",
            "last_name": "Test",
            "email": "test_admin_email@email.ru",
            "username": "Test2",
            "password": "PASSWORD",
            "phone_number": "1234567892",
            "call_availability": "Any time",
        },
    )

    admin = User.objects.get(email="test_admin_email@email.ru")
    admin.is_active, admin.is_staff, admin.is_superuser = True, True, True
    admin.status = UsersStatus.ACTIVE.value
    admin.role = UsersRole.ADMIN.value
    admin.save()

    return admin


@pytest.fixture
def admin_auth_token(admin, client) -> str:
    data = {"password": "PASSWORD", "email": admin.email}
    response = client().post(path="/api/auth/token/login/", data=data)
    return response.json().get("auth_token")


@pytest.fixture
def advertisement(city, category, user, client, auth_token) -> Advertisement:
    """Test create advertisement by user."""

    data = {
        "name": "Test name",
        "category": category.id,
        "city": city.id,
        "price": 30000,
        "description": "Test description",
        "images": [],
    }

    client().post(
        path="/api/ads/advertisements/",
        data=data,
        headers={"Authorization": f"Token {auth_token}"},
    )

    ad = Advertisement.objects.first()
    ad.status = AdvertisementStatus.ACTIVE.value
    ad.save()

    data = {
        "name": "Test name 2",
        "category": category.id,
        "city": city.id,
        "price": 30000,
        "description": "Test description 2",
        "images": [],
    }
    client().post(
        path="/api/ads/advertisements/",
        data=data,
        headers={"Authorization": f"Token {auth_token}"},
    )

    return ad


@pytest.fixture
def moderation_record(
    client, admin_auth_token, advertisement, admin
) -> ModerationRecordHistory:
    data = {
        "advertisement": advertisement.id,
        "moderator": admin.id,
        "decision": ModerationDecision.SEND_FOR_REVISION.value,
        "rejection_reason": "rejection_reason",
    }

    client().post(
        path="/api/ads/moderation_history/",
        data=data,
        headers={"Authorization": f"Token {admin_auth_token}"},
    )
    return ModerationRecordHistory.objects.first()


@pytest.fixture
def admin_headers(admin_auth_token):
    return {"Authorization": f"Token {admin_auth_token}"}


@pytest.fixture
def user_headers(auth_token):
    return {"Authorization": f"Token {auth_token}"}
