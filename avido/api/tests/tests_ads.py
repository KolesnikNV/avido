import pytest
from faker import Faker
from rest_framework import status

import api.consts as consts
from advertisement.enums import AdvertisementStatus, ModerationDecision
from advertisement.models import (
    Advertisement,
    AdvertisementCategory,
    City,
    ModerationRecordHistory,
    Region,
)

fake = Faker()

DATA = {
    "name": "Test name",
    "category": "",
    "city": "",
    "price": 30000,
    "description": "Test description",
    "images": [],
}
BASE_URL = "/api/ads"
BASE_ADS_URL = "/api/ads/advertisements/"


@pytest.mark.django_db
def test_create_region_and_city():
    """Test create region and city."""

    region_count_before = Region.objects.count()
    city_count_before = City.objects.count()

    region = Region.objects.create(name="Region")
    city = City.objects.create(name="City", region=region)

    assert Region.objects.count() == region_count_before + 1
    assert City.objects.count() == city_count_before + 1
    assert city.region == region


@pytest.mark.django_db
def test_create_category():
    """Test create category."""

    count_before = AdvertisementCategory.objects.count()

    future_parent_category = AdvertisementCategory.objects.create(
        name="Category 1",
        slug="category-1",
        description="description",
        sort_order=1,
        parent_category=None,
    )
    new_category = AdvertisementCategory.objects.create(
        name="Category 2",
        slug="category-2",
        description="description",
        sort_order=2,
        parent_category=future_parent_category,
    )

    assert AdvertisementCategory.objects.count() == count_before + 2
    assert (
        AdvertisementCategory.objects.get(name=future_parent_category.name)
        == future_parent_category
    )
    assert (
        AdvertisementCategory.objects.get(name=new_category.name)
        == new_category
    )


@pytest.mark.django_db
def test_create_advertisement(city, category, user):
    """Test create advertisement."""

    count_before = Advertisement.objects.count()

    advertisement_name = fake.text(max_nb_chars=20)
    advertisement_description = fake.text(max_nb_chars=status.HTTP_200_OK)
    advertisement_price = 30000

    Advertisement.objects.create(
        name=advertisement_name,
        description=advertisement_description,
        price=advertisement_price,
        views=1,
        status=AdvertisementStatus.ACTIVE.value,
        category=category,
        city=city,
        user=user,
    )

    created_advertisement = Advertisement.objects.last()

    assert Advertisement.objects.count() == count_before + 1
    assert created_advertisement.name == advertisement_name
    assert created_advertisement.description == advertisement_description
    assert created_advertisement.price == advertisement_price
    assert created_advertisement.category == category
    assert created_advertisement.city == city
    assert created_advertisement.user == user


@pytest.mark.django_db
def test_create_advertisement_by_user(
    city, category, user, client, user_headers
):
    """Test create advertisement by user."""

    count_before = Advertisement.objects.count()
    DATA["category"] = category.id
    DATA["city"] = city.id

    response = client().post(
        path=BASE_ADS_URL,
        data=DATA,
        format="json",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Advertisement.objects.count() == count_before + 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status, status_code, text_error, call_count",
    [
        (
            "active",
            status.HTTP_403_FORBIDDEN,
            consts.Message.UNCHANGEABLE.value,
            2,
        ),
        ("draft", status.HTTP_200_OK, None, 2),
    ],
)
def test_update_advertisement_by_user(
    city,
    category,
    user,
    client,
    user_headers,
    advertisement,
    status,
    status_code,
    text_error,
    call_count,
):
    """Test create advertisement by user."""

    DATA["name"] = DATA["name"] + "TEST"
    DATA["category"] = category.id
    DATA["city"] = city.id

    advertisement_id = Advertisement.objects.get(status=status).id

    response = client().put(
        path=f"{BASE_URL}/cabinet/{advertisement_id}/",
        data=DATA,
        headers=user_headers,
    )
    print(response.json())

    assert response.status_code == status_code
    assert response.data.get("detail") == text_error
    assert Advertisement.objects.count() == call_count


@pytest.mark.django_db
def test_delete_advertisement_by_user(
    user_headers, client, advertisement, user
):
    """Test delete advertisement by user."""

    count_before = Advertisement.objects.count()
    advertisement_id = Advertisement.objects.first().id

    response = client().delete(
        path=f"{BASE_URL}/cabinet/{advertisement_id}/",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert Advertisement.objects.count() == count_before


@pytest.mark.django_db
def test_get_advertisement_list(city, category, user, client, user_headers):
    """
    Test: Get Advertisement List
    One of the advertisements is a draft. This ad must not be listed.
    """

    count_before = Advertisement.objects.count()
    DATA["name"] = DATA["name"] + "TEST"
    DATA["category"] = category.id
    DATA["city"] = city.id

    client().post(
        path="/api/ads/advertisements/",
        data=DATA,
        headers=user_headers,
    )

    ad = Advertisement.objects.first()
    ad.status = AdvertisementStatus.ACTIVE.value
    ad.save()

    DATA["name"] = DATA["name"] + "TEST 2"

    client().post(
        path="/api/ads/advertisements/",
        data=DATA,
        headers=user_headers,
    )

    response = client().get(path=BASE_ADS_URL)

    assert response.status_code == status.HTTP_200_OK
    assert Advertisement.objects.count() == count_before + 2
    assert len(response.data) == Advertisement.objects.count() - 1


@pytest.mark.django_db
def test_get_category_by_admin(client, user_headers):
    """Test get categories."""

    response = client().get(
        path=f"{BASE_ADS_URL}categories/",
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_category_by_admin(client, admin_headers, category):
    """Test create category by admin."""

    count_before = AdvertisementCategory.objects.count()
    data = {
        "name": "Category 3",
        "slug": "category-3",
        "description": "description",
        "sort_order": 1,
        "parent_category": category.id,
    }

    response = client().post(
        path=f"{BASE_ADS_URL}categories/",
        data=data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert AdvertisementCategory.objects.count() == count_before + 1


@pytest.mark.django_db
def test_update_category_by_admin(client, admin_headers, category):
    """Test update category by admin."""

    count_before = AdvertisementCategory.objects.count()
    data = {
        "name": "Category 4",
        "slug": "category-4",
        "description": "description 4",
        "sort_order": 0,
        "parent_category": category.id,
    }
    advertisement_category_id = AdvertisementCategory.objects.first().id

    response = client().put(
        path=f"{BASE_ADS_URL}categories/{advertisement_category_id}/",
        data=data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert AdvertisementCategory.objects.count() == count_before


@pytest.mark.django_db
def test_delete_category_by_admin(client, admin_headers, category):
    """Test delete category by admin."""

    count_before = AdvertisementCategory.objects.count()
    response = client().delete(
        path=f"{BASE_ADS_URL}categories/{AdvertisementCategory.objects.first().id}/",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert AdvertisementCategory.objects.count() == count_before - 2


@pytest.mark.django_db
def test_create_moderation_record(client, admin_headers, advertisement, admin):
    """Test create moderation record."""

    count_before = ModerationRecordHistory.objects.count()
    data = {
        "advertisement": advertisement.id,
        "moderator": admin.id,
        "decision": ModerationDecision.SEND_FOR_REVISION.value,
        "rejection_reason": "rejection_reason",
    }

    response = client().post(
        path=f"{BASE_URL}/moderation_history/",
        data=data,
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert ModerationRecordHistory.objects.count() == count_before + 1


@pytest.mark.django_db
def test_get_moderation_record(client, moderation_record, admin_headers):
    """Test get moderation record."""

    response = client().get(
        path=f"{BASE_URL}/moderation_history/",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == ModerationRecordHistory.objects.count()


@pytest.mark.django_db
def test_update_moderation_record(
    client, moderation_record, admin_headers, advertisement, admin
):
    """Test update moderation record by admin."""

    count_before = ModerationRecordHistory.objects.count()
    data = {
        "advertisement": advertisement.id,
        "moderator": admin.id,
        "decision": ModerationDecision.SEND_FOR_REVISION.value,
        "rejection_reason": "rejection_reason 2",
    }

    response = client().put(
        path=f"{BASE_URL}/moderation_history/{moderation_record.id}/",
        headers=admin_headers,
        data=data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert ModerationRecordHistory.objects.count() == count_before


@pytest.mark.django_db
def test_delete_moderation_record(client, moderation_record, admin_headers):
    """Test delete moderation record by admin."""

    count_before = ModerationRecordHistory.objects.count()
    response = client().delete(
        path=f"{BASE_URL}/moderation_history/{moderation_record.id}/",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ModerationRecordHistory.objects.count() == count_before - 1
