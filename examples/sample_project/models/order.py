"""Order model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class OrderStatus(Enum):
    """Order status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Order entity."""

    user_id: str
    amount: float
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = field(default=OrderStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.now)

    def complete(self) -> None:
        """Mark order as completed."""
        self.status = OrderStatus.COMPLETED

    def cancel(self) -> None:
        """Cancel the order."""
        if self.status == OrderStatus.COMPLETED:
            raise ValueError("Cannot cancel completed order")
        self.status = OrderStatus.CANCELLED
