from typing import List, Tuple, Type

from django.db.models import QuerySet
from django.http import Http404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

import api.consts as consts
import api.serializers as slr
from advertisement import models
from advertisement.enums import AdvertisementStatus
from advertisement.filters import AdvertisementFilter
from api.permissions import IsStaff, IsStaffOrReadOnly
from avido.elastic_config import index_advertisement, search_description
from users.db_utils import (
    delete_token_for_confirm_email,
    get_user_by_email,
    get_user_by_token,
    choose_confirm_registration_strategy,
)
from users.models import RegistrationToken, UsersStatus
from users.tasks import get_and_set_random_avatar, send_confirmation_email


class RegistrationView(
    viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin
):
    """Support `create()` method."""

    serializer_class = slr.CreateUserSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        email = request.data["email"]
        token = get_random_string(length=16)
        user = get_user_by_email(email)

        get_and_set_random_avatar.delay(email)
        send_confirmation_email.delay(
            [email],
            request.build_absolute_uri(
                reverse(
                    choose_confirm_registration_strategy(user),
                    kwargs={"token": token},
                )
            ),
        )

        RegistrationToken.objects.create(user=user, token=token)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConfirmRegistrationView(APIView):
    def get_and_activate_user(self, token):
        user = get_user_by_token(token)
        user.status = UsersStatus.ACTIVE.value
        user.is_active = True

        return user

    def get(self, request: Request, token: str) -> Response:
        """
        The user follows the link from the email.
        A token is taken from the url and compared with what is in the database.
        If the token is correct, the user's status is changed
        and the used token is deleted.
        """

        user = self.get_and_activate_user(token)
        user.save()

        delete_token_for_confirm_email(token)

        return Response(
            consts.Message.SUCCESS_CONFIRM_EMAIL.value,
            status=status.HTTP_200_OK,
        )


class SetPasswordView(ConfirmRegistrationView):
    """Class for set password after registration by admin."""

    serializer_class = slr.SetPasswordSerializer

    def post(self, request: Request, token: str) -> Response:
        """
        The user follows the link from the email.
        A token is taken from the url and compared with what is in the database.
        If the token is correct, the user's status is changed
        and the used token is deleted.
        """

        user = self.get_and_activate_user(token)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["password"])
        user.save()

        delete_token_for_confirm_email(token)

        return Response(
            consts.Message.SUCCESS_CONFIRM_EMAIL.value,
            status=status.HTTP_200_OK,
        )


class AdvertisementView(viewsets.GenericViewSet, generics.ListCreateAPIView):
    """ViewSet for get and create Advertisements."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdvertisementFilter

    def get_queryset(self) -> QuerySet:
        return (
            models.Advertisement.objects.select_related("user")
            if self.request.user.is_staff
            else models.Advertisement.objects.select_related("user").filter(
                status=AdvertisementStatus.ACTIVE.value
            )
        )

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        return (
            slr.CreateAdvertisementSerializer
            if self.request.method == "POST"
            else slr.ListAdvertisementsSerializer
        )

    def get_permissions(self) -> Tuple[BasePermission]:
        return (
            (IsAuthenticated(),)
            if self.request.method == "POST"
            else (AllowAny(),)
        )

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        name_query = request.query_params.get("name", "")
        description_query = request.query_params.get("description", "")

        index_advertisement(queryset)

        if name_query or description_query:
            search_results = search_description(name_query, description_query)
            found_advertisement_ids = [
                hit["_source"]["id"] for hit in search_results
            ]
            queryset = queryset.filter(pk__in=found_advertisement_ids)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                slr.DetailAdvertisementsSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvertisementDetailView(
    viewsets.GenericViewSet, generics.RetrieveAPIView
):
    """ViewSet for get one Advertisement record."""

    permission_classes = (AllowAny,)
    queryset = models.Advertisement.objects.filter(
        status=AdvertisementStatus.ACTIVE.value
    )
    serializer_class = slr.DetailAdvertisementsSerializer

    def get_object(self) -> models.Advertisement | Http404:
        return get_object_or_404(self.queryset, pk=self.kwargs["pk"])

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        viewed_ads = request.session.get("viewed_ads", [])

        if instance.pk not in viewed_ads and instance.user != request.user:
            instance.views += 1
            instance.save()
            viewed_ads.append(instance.pk)
            request.session["viewed_ads"] = viewed_ads

        return Response(serializer.data)


class PersonalCabinetView(
    viewsets.GenericViewSet,
    generics.ListAPIView,
    generics.RetrieveAPIView,
    generics.DestroyAPIView,
):
    """ViewSet for get Personal Cabinet."""

    def get_queryset(self) -> List[models.Advertisement]:
        return models.Advertisement.objects.filter(user=self.request.user)

    def get_serializer_class(
        self,
    ) -> Type[
        slr.CreateAdvertisementSerializer | slr.ListAdvertisementsSerializer
    ]:
        return (
            slr.CreateAdvertisementSerializer
            if self.request.method == "PUT"
            else slr.ListAdvertisementsSerializer
        )

    def get_object(self) -> PermissionDenied | models.Advertisement:
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()

        is_published = instance.status not in (
            AdvertisementStatus.DRAFT.value,
            AdvertisementStatus.REJECTED.value,
        )

        if is_published:
            raise PermissionDenied(detail=consts.Message.UNCHANGEABLE.value)

        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(
            slr.DetailAdvertisementsSerializer(instance).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, *args, **kwargs):
        instance = self.get_object()
        instance.status = AdvertisementStatus.SOLD.value
        instance.save()

        return Response(status=status.HTTP_200_OK)


class UnlistAdvertisementView(generics.DestroyAPIView):
    """ViewSet for unlist Advertisement."""

    serializer_class = slr.DetailAdvertisementsSerializer

    def get_queryset(self) -> List[models.Advertisement]:
        return models.Advertisement.objects.filter(user=self.request.user)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()

        if instance.status != AdvertisementStatus.ACTIVE.value:
            return Response(
                {"detail": consts.Message.NOT_ACTIVE_AD.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.status = AdvertisementStatus.SOLD.value
        instance.save()

        return Response(
            {"detail": consts.Message.ALREADY_SOLED.value},
            status=status.HTTP_200_OK,
        )


class AdvertisementCategoryView(
    viewsets.GenericViewSet,
    generics.ListCreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """ViewSet for get and create AdvertisementCategories."""

    serializer_class = slr.CreateAdvertisementCategorySerializer
    queryset = models.AdvertisementCategory.objects.filter(parent_category=None)
    permission_classes = (IsStaffOrReadOnly,)

    def get_serializer_class(
        self,
    ) -> Type[
        slr.CreateAdvertisementCategorySerializer
        | slr.ListAdvertisementCategoriesSerializer
    ]:
        return (
            slr.CreateAdvertisementCategorySerializer
            if self.request.method in ("POST", "PUT")
            else slr.ListAdvertisementCategoriesSerializer
        )

    def get_object(self) -> PermissionDenied | models.Advertisement:
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])


class RegionView(viewsets.GenericViewSet, generics.ListCreateAPIView):
    """ViewSet for get and create Region."""

    serializer_class = slr.CreateRegionSerializer
    queryset = models.Region.objects.all()
    permission_classes = (IsStaffOrReadOnly,)


class CityView(viewsets.GenericViewSet, generics.ListCreateAPIView):
    """ViewSet for get and create City."""

    serializer_class = slr.CreateCitySerializer
    queryset = models.City.objects.all()
    permission_classes = (IsStaffOrReadOnly,)


class ModerationRecordHistoryView(
    viewsets.GenericViewSet,
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """ViewSet for listing and create ModerationRecordHistory."""

    serializer_class = slr.ModerationRecordHistorySerializer
    permission_classes = (IsStaff,)

    def get_queryset(
        self,
    ) -> List[models.ModerationRecordHistory | models.AdvertisementCategory]:
        return (
            models.AdvertisementCategory.objects.filter(
                status=AdvertisementStatus.MODERATION.value
            )
            if self.request.method == "POST"
            else models.ModerationRecordHistory.objects.all()
        )
