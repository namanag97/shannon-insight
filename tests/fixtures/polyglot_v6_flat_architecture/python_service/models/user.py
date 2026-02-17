"""User model - depth 0, no imports."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str

    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"
