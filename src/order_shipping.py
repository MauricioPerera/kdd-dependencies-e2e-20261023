"""Compute shipping from the validated total quantity."""
from .order_input import normalize_items


def shipping(items: object) -> int:
    units = sum(quantity for _, quantity, _ in normalize_items(items))
    return 0 if units >= 6 else 250 + 75 * (units - 1)
