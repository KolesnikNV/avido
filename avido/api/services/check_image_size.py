from io import BytesIO

from PIL import Image
from rest_framework import serializers

from api import consts

MAX_IMAGE_SIZE = 1500


def check_image_size(image_content: bytes) -> None:
    """Check weight and height of image."""

    pil_image = Image.open(BytesIO(image_content))
    width, height = pil_image.size

    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        raise serializers.ValidationError(
            consts.Message.CANNOT_UPLOAD_IMAGE.value
        )
