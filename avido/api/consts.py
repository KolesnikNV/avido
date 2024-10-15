from enum import Enum


class Message(Enum):
    """Messages text."""

    UNCHANGEABLE = "Нельзя изменить объявление, которое уже было одобрено!"
    NOT_ACTIVE_AD = "Это объявление уже не активно"
    ALREADY_SOLED = "Объявление успешно снято с продажи."
    SUCCESS_CONFIRM_EMAIL = "Email подтвержден успешно!"
    CANNOT_UPLOAD_IMAGE = (
        "Размер изображения превышает максимально "
        "допустимый размер (1500x1500)."
    )

    MIN_COUNT_ADVERTISEMENT_IN_DB = 20


class ApiUrls(Enum):
    DOG_URL = "https://dog.ceo/api/breeds/image/random"
    CAT_URL = "https://api.thecatapi.com/v1/images/search"
