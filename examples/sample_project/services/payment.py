"""Payment service."""

from utils.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    """Handles payment processing."""

    def __init__(self) -> None:
        self._gateway = "stripe"

    def charge(self, user_id: str, amount: float) -> bool:
        """Charge user for amount."""
        logger.info(f"Charging {user_id}: ${amount}")
        return True

    def refund(self, user_id: str, amount: float) -> bool:
        """Refund amount to user."""
        logger.info(f"Refunding {user_id}: ${amount}")
        return True

    def get_balance(self, user_id: str) -> float:
        """Get user balance."""
        return 0.0
