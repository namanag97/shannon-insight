"""
Simple, clean Python code - low complexity, high quality
"""


class UserProcessor:
    """Process user data efficiently."""

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def validate(self) -> bool:
        """Validate user data."""
        if not self.name or len(self.name) < 2:
            return False
        if not self.email or "@" not in self.email:
            return False
        return True

    def format_email(self) -> str:
        """Format email for display."""
        return self.email.lower().strip()

    def get_full_name(self) -> str:
        """Get formatted full name."""
        return self.name.strip().title()


def process_user(name: str, email: str) -> dict:
    """Process a user and return formatted data."""
    processor = UserProcessor(name, email)

    if not processor.validate():
        return {"valid": False, "error": "Invalid user data"}

    return {
        "valid": True,
        "name": processor.get_full_name(),
        "email": processor.format_email(),
    }
