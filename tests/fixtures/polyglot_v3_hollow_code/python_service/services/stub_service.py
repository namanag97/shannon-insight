"""Service with placeholder implementations - triggers HOLLOW_CODE."""


def process_order(order_id: str) -> dict:
    pass  # STUB


def validate_payment(amount: float) -> bool: ...  # STUB


def calculate_tax(subtotal: float) -> float:
    raise NotImplementedError()  # STUB


def format_receipt(order: dict) -> str:
    return None  # STUB


def send_confirmation(email: str) -> None:
    pass  # STUB


def log_transaction(data: dict) -> None:
    """Implemented function for gini variance."""
    import json

    formatted = json.dumps(data, indent=2)
    for line in formatted.split("\n"):
        if line.strip():
            print(line)
