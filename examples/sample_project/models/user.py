"""User model."""

from dataclasses import dataclass, field
from uuid import uuid4

from utils.validators import validate_email


@dataclass
class User:
    """User entity."""

    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid4()))
    is_active: bool = True

    def __post_init__(self) -> None:
        validate_email(self.email)

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
