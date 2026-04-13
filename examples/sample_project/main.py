"""Main entry point for the sample project."""

from models.user import User
from models.order import Order
from services.auth import AuthService
from services.payment import PaymentService
from utils.logger import get_logger

logger = get_logger(__name__)


class Application:
    """Main application class."""

    def __init__(self) -> None:
        self.auth_service = AuthService()
        self.payment_service = PaymentService()
        self.users: dict[str, User] = {}
        self.orders: dict[str, Order] = {}

    def run(self) -> None:
        """Run the application."""
        logger.info("Starting application")
        self._setup_routes()
        self._start_server()

    def _setup_routes(self) -> None:
        """Setup application routes."""
        from api.routes import setup_routes
        setup_routes(self)

    def _start_server(self) -> None:
        """Start the HTTP server."""
        logger.info("Server started on port 8080")

    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user = User(name=name, email=email)
        self.users[user.id] = user
        logger.info(f"Created user: {user.id}")
        return user

    def create_order(self, user_id: str, amount: float) -> Order:
        """Create a new order for a user."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        order = Order(user_id=user_id, amount=amount)
        self.orders[order.id] = order
        logger.info(f"Created order: {order.id}")
        return order

    def process_payment(self, order_id: str) -> bool:
        """Process payment for an order."""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        return self.payment_service.charge(order.user_id, order.amount)


def main() -> None:
    """Main entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
