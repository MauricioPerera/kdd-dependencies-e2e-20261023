"""Compute an integer subtotal from validated order lines."""
from .order_input import normalize_items


def subtotal(items: object) -> int:
    return sum(quantity * price for _, quantity, price in normalize_items(items))
