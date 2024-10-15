from enum import Enum


class AdvertisementStatus(Enum):
    """Enum for advertisement statuses."""

    DRAFT: str = "draft"
    MODERATION: str = "moderation"
    REJECTED: str = "rejected"
    SOLD: str = "sold"
    ACTIVE: str = "active"


class ModerationDecision(Enum):
    """Enum to represent moderation decisions."""

    PUBLISH: str = "publish"
    SEND_FOR_REVISION: str = "send_for_revision"
