from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from api.services.avatar import avatar
from users.db_utils import get_user_by_email


@shared_task(name="send_email", acks_late=True, autoretry_for=(Exception,))
def send_confirmation_email(email: str, link: str) -> None:
    """Celery task for sending email for reset password."""

    send_mail(
        "Подтверждение email",
        f"Для регистрации необходимо пройти по ссылке - {link}",
        settings.EMAIL_HOST_USER,
        email,
    )


@shared_task(name="avatar", acks_late=True, autoretry_for=(Exception,))
def get_and_set_random_avatar(email: str) -> None:
    """Celery task for getting random avatar and setting it to user."""

    avatar.set_avatar(get_user_by_email(email))
