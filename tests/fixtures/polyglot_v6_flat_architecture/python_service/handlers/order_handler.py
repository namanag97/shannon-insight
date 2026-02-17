"""Order handler - depth 1, imports models directly (no glue layer)."""

from datetime import datetime

from ..models.order import Order


def get_order(order_id: int) -> Order:
    """Get order by ID - direct model access."""
    return Order(id=order_id, user_id=1, total=99.99, created_at=datetime.now())


def create_order(user_id: int, total: float) -> Order:
    """Create order - direct model instantiation."""
    return Order(id=1, user_id=user_id, total=total, created_at=datetime.now())


def list_orders(user_id: int) -> list:
    """List orders for user."""
    return [
        Order(id=1, user_id=user_id, total=50.0, created_at=datetime.now()),
        Order(id=2, user_id=user_id, total=75.0, created_at=datetime.now()),
    ]
