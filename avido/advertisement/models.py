from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User

from .enums import AdvertisementStatus, ModerationDecision


class AdvertisementCategory(models.Model):
    """Class to represent advertisement categories."""

    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"))
    description = models.TextField(_("Description"))
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("Parent Category"),
        null=True,
        blank=True,
    )
    sort_order = models.IntegerField(
        _("Sort Order"), choices=[(0, "ASC"), (1, "DESC")], default=0
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Advertisement(models.Model):
    """Class to represent an advertisement."""

    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=1)
    views = models.IntegerField(_("Views"), default=0)
    status = models.CharField(
        _("Status"),
        choices=[(role.value, role.name) for role in AdvertisementStatus],
        default=AdvertisementStatus.DRAFT.value,
        max_length=30,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now_add=True)
    category = models.ForeignKey(
        AdvertisementCategory,
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        related_name="advertisements",
    )
    city = models.ForeignKey(
        "advertisement.City",
        on_delete=models.CASCADE,
        verbose_name=_("City"),
        related_name="advertisements",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="advertisements"
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return self.name


class AdvertisementImages(models.Model):
    """Class to represent images."""

    image = models.BinaryField(_("Image"))
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return f"{self.advertisement} - {self.image}"


class Region(models.Model):
    """Model to represent a region."""

    name = models.CharField(_("Name"), max_length=100, unique=True)

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"

    def __str__(self):
        return self.name


class City(models.Model):
    """Model to represent a city."""

    name = models.CharField(_("Name"), max_length=100, unique=True)

    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, verbose_name=_("Region")
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name


class ModerationRecordHistory(models.Model):
    """Model to represent a moderation record for an advertisement."""

    moderation_date = models.DateTimeField(
        _("Moderation Date"), auto_now_add=True
    )
    advertisement = models.ForeignKey(
        "Advertisement",
        on_delete=models.CASCADE,
        verbose_name=_("Advertisement"),
    )
    moderator = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name=_("Moderator")
    )
    decision = models.CharField(
        _("Decision"),
        choices=[
            (decision.value, decision.name) for decision in ModerationDecision
        ],
        default=ModerationDecision.PUBLISH.value,
        max_length=30,
    )

    rejection_reason = models.TextField(_("Rejection Reason"), blank=True)

    class Meta:
        verbose_name = "История модерации"

    def __str__(self):
        return f"{self.advertisement} - {self.moderation_date}"
