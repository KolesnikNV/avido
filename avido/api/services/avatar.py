import random


import api.consts as consts
import requests


class Avatar:
    """Avatar class."""

    @staticmethod
    def get_dog_photo() -> str:
        """Get random dog photo from free api."""

        return requests.get(consts.ApiUrls.DOG_URL.value).json()["message"]

    @staticmethod
    def get_cat_photo() -> str:
        """Get random cat photo from free api."""

        return requests.get(consts.ApiUrls.CAT_URL.value).json()[0]["url"]

    def get_random_avatar(self) -> bytes:
        """Get random avatar for both api."""

        image = random.choice([self.get_dog_photo(), self.get_cat_photo()])
        return requests.get(image).content

    def set_avatar(self, user) -> None:
        """Set avatar for user."""

        user.avatar = self.get_random_avatar()
        user.save()


avatar = Avatar()
