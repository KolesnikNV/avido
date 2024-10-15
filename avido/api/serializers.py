import base64

from django.forms import ModelChoiceField
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from transliterate import translit

from advertisement.models import (
    Advertisement,
    AdvertisementCategory,
    AdvertisementImages,
    City,
    ModerationRecordHistory,
    Region,
)
from api.services.check_image_size import check_image_size
from users.db_utils import create_user
from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer creating a new user."""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "phone_number",
            "call_availability",
        )
        extra_kwargs = {
            "email": {"write_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data: dict):
        """User creation logic."""

        return create_user(
            *[
                validated_data[field]
                for field in CreateUserSerializer.Meta.fields
            ]
        )


class SetPasswordSerializer(serializers.Serializer):
    """Serializer for setting the password."""

    password = serializers.CharField(min_length=8)
    repeat_password = serializers.CharField(min_length=8)


class ImagesSerializer(serializers.ModelSerializer):
    """Serializer listing advertisement's images."""

    class Meta:
        model = AdvertisementImages
        fields = ("image", "advertisement")


class CreateRegionSerializer(serializers.ModelSerializer):
    """Serializer creating a new Region."""

    class Meta:
        model = Region
        fields = ("name",)


class CreateCitySerializer(serializers.ModelSerializer):
    """Serializer creating a new City."""

    region = ModelChoiceField(queryset=Region.objects.all(), required=True)

    class Meta:
        model = City
        fields = ("name", "region")


class ListCitySerializer(serializers.ModelSerializer):
    """Serializer listing a new City."""

    class Meta:
        model = City
        fields = ("name",)


class ListCategorySerializer(serializers.ModelSerializer):
    """Serializer listing Categories"""

    class Meta:
        model = AdvertisementCategory
        fields = ("name",)


class ListAdvertisementsSerializer(serializers.ModelSerializer):
    """Serializer listing all advertisements."""

    category = ListCategorySerializer(read_only=True)
    city = ListCitySerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = (
            "name",
            "category",
            "city",
            "price",
            "created_at",
            "updated_at",
            "price",
            "views",
            "image",
        )

    def get_image(self, obj):
        """Method for custom serializer field."""

        images = obj.images.first()
        return ImagesSerializer(images, many=False).data


class DetailAdvertisementsSerializer(serializers.ModelSerializer):
    """Serializer listing all advertisements."""

    city = ListCitySerializer(read_only=True)
    user = CreateUserSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    category = ListCategorySerializer(read_only=True)

    class Meta:
        model = Advertisement
        fields = (
            "name",
            "category",
            "city",
            "price",
            "created_at",
            "updated_at",
            "description",
            "price",
            "views",
            "user",
            "images",
        )

    def get_images(self, obj):
        """Method for custom serializer field."""

        return ImagesSerializer(obj.images.all(), many=True).data


class CreateAdvertisementSerializer(serializers.ModelSerializer):
    """Serializer creating a new Advertisement."""

    user = serializers.HiddenField(default=CurrentUserDefault())
    views = serializers.HiddenField(default=0)
    images = serializers.ListField(
        child=serializers.ImageField(), required=False
    )

    class Meta:
        model = Advertisement
        fields = (
            "name",
            "category",
            "city",
            "price",
            "description",
            "price",
            "views",
            "user",
            "images",
        )

    def create(self, validated_data: dict) -> Advertisement:
        images = validated_data.pop("images", None)
        advertisement = Advertisement.objects.create(**validated_data)

        if images:
            for image in images:
                image_content = image.read()

                check_image_size(image_content)

                AdvertisementImages.objects.create(
                    image=image_content,
                    advertisement=advertisement,
                )

        return advertisement


class CreateAdvertisementCategorySerializer(serializers.ModelSerializer):
    """Serializer creating a new AdvertisementCategory."""

    parent_category = ModelChoiceField(
        queryset=AdvertisementCategory.objects.all(), required=False
    )

    class Meta:
        model = AdvertisementCategory
        fields = ("name", "description", "parent_category", "sort_order")

    def create(self, validated_data: dict) -> AdvertisementCategory:
        validated_data["slug"] = slugify(
            translit(validated_data.get("name"), "ru", reversed=True)
        )

        return super().create(validated_data)


class ListAdvertisementCategoriesSerializer(serializers.ModelSerializer):
    """Serializer listing all advertisement categories."""

    children = serializers.SerializerMethodField()

    class Meta:
        model = AdvertisementCategory
        fields = (
            "name",
            "children",
        )

    def get_children(self, obj):
        """Method for getting categories as tree."""

        def get_children_recursively(category):
            children = AdvertisementCategory.objects.filter(
                parent_category=category
            )
            child_data = []

            for child in children:
                child_data.append(
                    {
                        "id": child.id,
                        "name": child.name,
                        "children": get_children_recursively(child),
                    }
                )
            return child_data

        return get_children_recursively(obj)


class ModerationRecordHistorySerializer(serializers.ModelSerializer):
    """Serializer for advertisement moderation history."""

    class Meta:
        model = ModerationRecordHistory
        fields = (
            "advertisement",
            "moderator",
            "decision",
            "rejection_reason",
        )
