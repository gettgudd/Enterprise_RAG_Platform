"""Role-Based Access Control (RBAC) data structures and validation."""

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


ROLE_PERMISSIONS: dict[Role, set[AccessLevel]] = {
    Role.ADMIN: {
        AccessLevel.PUBLIC,
        AccessLevel.INTERNAL,
        AccessLevel.CONFIDENTIAL,
        AccessLevel.RESTRICTED,
    },
    Role.MANAGER: {
        AccessLevel.PUBLIC,
        AccessLevel.INTERNAL,
        AccessLevel.CONFIDENTIAL,
    },
    Role.EMPLOYEE: {
        AccessLevel.PUBLIC,
        AccessLevel.INTERNAL,
    },
}


@dataclass
class UserContext:
    user_id: str
    username: str
    role: Role
    department: str


def has_access(user: UserContext, document_access_level: str | AccessLevel) -> bool:
    """Verify if a user context permits accessing a document with the given access level."""
    try:
        level = AccessLevel(document_access_level.lower())
    except ValueError:
        return False

    allowed_levels = ROLE_PERMISSIONS.get(user.role, set())
    return level in allowed_levels
