from django.contrib import admin

from .models import (
    Advertisement,
    AdvertisementCategory,
    AdvertisementImages,
    City,
    ModerationRecordHistory,
    Region,
)


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Class for advertisement admin."""

    search_fields = (
        "name",
        "status",
    )
    list_display = (
        "name",
        "status",
        "category",
    )
    list_filter = (
        "name",
        "status",
        "category",
    )


@admin.register(AdvertisementImages)
class AdvertisementImagesAdmin(admin.ModelAdmin):
    """Class for advertisement images admin."""

    search_fields = ("advertisement",)
    list_display = ("advertisement",)
    list_filter = ("advertisement",)


@admin.register(ModerationRecordHistory)
class ModerationRecordHistoryAdmin(admin.ModelAdmin):
    """Class for moderation record history admin."""

    search_fields = ("decision",)
    list_display = (
        "moderator",
        "decision",
    )
    list_filter = (
        "moderator",
        "decision",
    )


@admin.register(AdvertisementCategory)
class AdvertisementCategoryAdmin(admin.ModelAdmin):
    """Class for advertisement category admin."""

    search_fields = (
        "name",
        "parent_category",
    )
    list_display = (
        "name",
        "parent_category",
    )
    list_filter = (
        "name",
        "parent_category",
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Class for city admin."""

    search_fields = (
        "name",
        "region",
    )
    list_display = (
        "name",
        "region",
    )
    list_filter = (
        "name",
        "region",
    )


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """Class for region admin."""

    search_fields = ("name",)
    list_display = ("name",)
    list_filter = ("name",)
