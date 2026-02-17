"""Notification service - imports email_sender but never changes with it.

This file has many commits by Alice, while email_sender has commits by Bob.
They never change on the same day despite the import relationship.
This triggers the DEAD_DEPENDENCY pattern.
"""

from ..utils.email_sender import send_email, EmailConfig


class NotificationService:
    """Service for sending notifications."""

    def __init__(self, config: EmailConfig):
        self.config = config

    def notify_user(self, user_id: int, message: str) -> bool:
        """Send notification to user."""
        # Uses email_sender but was written by different author
        # and never changes when email_sender changes
        email = f"user{user_id}@example.com"
        return send_email(email, "Notification", message, self.config)

    def notify_admin(self, message: str) -> bool:
        """Send notification to admin."""
        return send_email("admin@example.com", "Admin Alert", message, self.config)

    def batch_notify(self, user_ids: list, message: str) -> dict:
        """Send notification to multiple users."""
        results = {}
        for user_id in user_ids:
            results[user_id] = self.notify_user(user_id, message)
        return results


# Added by Alice - commit 1
def format_notification(title: str, body: str) -> str:
    return f"[{title}] {body}"


# Added by Alice - commit 2
def validate_notification(message: str) -> bool:
    return len(message) > 0 and len(message) < 1000


# Added by Alice - commit 3
def log_notification(user_id: int, message: str) -> None:
    print(f"Notified user {user_id}: {message[:50]}...")
