"""Model file for testing MODEL role detection."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Status(Enum):
    """Status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class User:
    """User model."""

    id: int
    name: str
    email: str
    status: Status = Status.PENDING


@dataclass
class Project:
    """Project model."""

    id: int
    title: str
    description: Optional[str] = None
    owner: Optional[User] = None
    members: List[User] = None

    def __post_init__(self):
        if self.members is None:
            self.members = []


@dataclass
class Task:
    """Task model."""

    id: int
    project_id: int
    title: str
    assignee: Optional[User] = None
    status: Status = Status.PENDING
