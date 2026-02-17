"""Main entry point - flat architecture, handlers directly use models."""

from .handlers.user_handler import create_user, get_user, list_users
from .handlers.order_handler import create_order, get_order, list_orders


def main():
    """Main function demonstrating flat architecture."""
    # No service layer, no glue - handlers directly access models
    user = create_user("Test", "test@example.com")
    print(f"Created user: {user.display_name()}")

    order = create_order(user.id, 99.99)
    print(f"Created order: {order.id}")

    users = list_users()
    orders = list_orders(user.id)
    print(f"Found {len(users)} users and {len(orders)} orders")


if __name__ == "__main__":
    main()
