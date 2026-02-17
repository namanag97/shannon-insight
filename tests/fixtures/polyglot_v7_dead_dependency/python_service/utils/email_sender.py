"""Email sender utility - commits by Bob, never co-changes with notification_service.

This file is imported by notification_service but they never change together.
Bob maintains this file while Alice maintains notification_service.
This triggers the DEAD_DEPENDENCY pattern.
"""

from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Email configuration."""

    smtp_host: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True


def send_email(to: str, subject: str, body: str, config: EmailConfig) -> bool:
    """Send an email using the provided configuration."""
    # Simulated email sending
    print(f"Sending email to {to}: {subject}")
    return True


# Added by Bob - commit 1
def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email


# Added by Bob - commit 2
def format_html_email(body: str) -> str:
    """Format email body as HTML."""
    return f"<html><body>{body}</body></html>"


# Added by Bob - commit 3
def get_default_config() -> EmailConfig:
    """Get default email configuration."""
    return EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        username="noreply",
        password="secret",
    )


# Added by Bob - commit 4
def batch_send(emails: list, subject: str, body: str, config: EmailConfig) -> dict:
    """Send email to multiple recipients."""
    return {email: send_email(email, subject, body, config) for email in emails}
