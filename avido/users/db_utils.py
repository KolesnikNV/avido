from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.utils.crypto import get_random_string

from users.models import RegistrationToken, User


def create_user(
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone_number: str,
    call_availability: str,
) -> User:
    """Creates a user in the database."""

    return User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        password=make_password(password),
        call_availability=call_availability,
    )


def get_user_by_email(email: str) -> User | None:
    """Receives a user from the Users table by email."""

    return User.objects.get(email=email)


def create_token(user: User) -> RegistrationToken:
    """Creates a unique token for email confirmation."""

    return RegistrationToken.objects.create(
        user=user, token=get_random_string(length=16)
    )


def get_user_by_token(token: str) -> User | bool:
    """Gets the user from the PasswordResetToken table by token."""

    user = RegistrationToken.objects.filter(token=token).last()

    if not user:
        raise Http404("Невалидный или устаревший токен!")

    return user.user


def delete_token_for_confirm_email(token: str) -> bool:
    """Deletes a token entry from the PasswordResetToken table."""

    if token_instance := RegistrationToken.objects.filter(token=token).first():
        token_instance.delete()
        return True

    return False


def check_if_user_have_password(user: User) -> bool:
    """Checks if the user has a password."""

    return bool(user.password)


def choose_confirm_registration_strategy(user) -> str:
    """Chooses the strategy for confirming the registration."""

    if check_if_user_have_password(user):
        return "api:register_confirm"

    return "api:set_password"
