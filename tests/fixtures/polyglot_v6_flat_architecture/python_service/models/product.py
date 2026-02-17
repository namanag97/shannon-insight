"""Product model - depth 0, no imports."""

from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int

    def is_available(self) -> bool:
        return self.stock > 0
