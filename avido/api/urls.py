from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    AdvertisementCategoryView,
    AdvertisementDetailView,
    AdvertisementView,
    CityView,
    ConfirmRegistrationView,
    ModerationRecordHistoryView,
    PersonalCabinetView,
    RegionView,
    RegistrationView,
    SetPasswordView,
)

app_name = "api"
users_router = DefaultRouter()
advertisement_router = DefaultRouter()

users_router.register(r"register", RegistrationView, basename="users")

advertisement_router.register(
    r"moderation_history",
    ModerationRecordHistoryView,
    basename="moderation_history",
)
advertisement_router.register(
    r"cabinet", PersonalCabinetView, basename="cabinet"
)
advertisement_router.register(
    r"advertisements/categories",
    AdvertisementCategoryView,
    basename="categories",
)
advertisement_router.register(
    r"advertisements/regions", RegionView, basename="regions"
)
advertisement_router.register(
    r"advertisements/cities", CityView, basename="cities"
)
advertisement_router.register(
    r"advertisements", AdvertisementView, basename="advertisements"
)
advertisement_router.register(
    r"advertisements",
    AdvertisementDetailView,
    basename="advertisement_detail",
)


urlpatterns = [
    path(
        "register/set_password/<str:token>",
        SetPasswordView.as_view(),
        name="set_password",
    ),
    path("auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path("", include(users_router.urls)),
    path("ads/", include(advertisement_router.urls)),
    path(
        "register/confirm/<str:token>",
        ConfirmRegistrationView.as_view(),
        name="register_confirm",
    ),
]
