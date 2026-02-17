"""Order model - depth 0, no imports."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    id: int
    user_id: int
    total: float
    created_at: datetime

    def is_paid(self) -> bool:
        return self.total > 0
