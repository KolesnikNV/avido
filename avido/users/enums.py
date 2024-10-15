from enum import Enum


class UsersRole(Enum):
    """Users role for User.role field."""

    USER: str = "user"
    MODERATOR: str = "moderator"
    ADMIN: str = "admin"


class UsersStatus(Enum):
    """Users status for User.status field."""

    BLOCKED: str = "blocked"
    ACTIVE: str = "active"
    WAITING_ACTIVATION: str = "waiting_activation"
