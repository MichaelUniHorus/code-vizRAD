"""Authentication service."""

from models.user import User
from utils.crypto import hash_password, verify_password
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Handles user authentication."""

    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}  # token -> user_id

    def authenticate(self, email: str, password: str) -> str | None:
        """Authenticate user and return token."""
        # Simplified for demo
        logger.info(f"Authenticating {email}")
        return "dummy_token"

    def register(self, user: User, password: str) -> bool:
        """Register a new user."""
        hashed = hash_password(password)
        logger.info(f"Registered user: {user.id}")
        return True

    def verify_token(self, token: str) -> str | None:
        """Verify token and return user_id."""
        return self._tokens.get(token)
