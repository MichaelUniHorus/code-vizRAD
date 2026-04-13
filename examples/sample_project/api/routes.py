"""API routes."""

from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from main import Application

logger = get_logger(__name__)


def setup_routes(app: "Application") -> None:
    """Setup application routes."""
    logger.info("Setting up routes")

    # Simplified route setup for demo
    routes = [
        ("/users", "user_handler"),
        ("/orders", "order_handler"),
        ("/auth", "auth_handler"),
        ("/payments", "payment_handler"),
    ]

    for path, handler in routes:
        logger.debug(f"Registered: {path} -> {handler}")
