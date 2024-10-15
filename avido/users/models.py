from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import UsersRole, UsersStatus


class User(AbstractUser):
    """
    Custom user model of the user.
    Username and email fields are required and must be unique.
    """

    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("First name"), max_length=150, blank=False)
    last_name = models.CharField(_("Last name"), max_length=150, blank=False)
    avatar = models.BinaryField(_("Avatar"), blank=True)
    email = models.EmailField(_("Email"), max_length=255, unique=True)
    role = models.CharField(
        _("Role"),
        choices=[(role.value, role.name) for role in UsersRole],
        default=UsersRole.USER.value,
        max_length=30,
    )
    phone_number = models.CharField(
        _("Phone number"), max_length=20, blank=False, unique=True
    )
    call_availability = models.CharField(
        _("Call Availability"), blank=False, null=False, max_length=30
    )
    status = models.CharField(
        _("Status"),
        choices=[(status.value, status.name) for status in UsersStatus],
        default=UsersStatus.WAITING_ACTIVATION.value,
        max_length=30,
    )
    is_active = models.BooleanField(_("Active"), default=False)
    last_login = date_joined = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email}"


class RegistrationToken(models.Model):
    """
    Data model for generating tokens for continue registration.
    It is used when sending an email message with a link to password recovery.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
