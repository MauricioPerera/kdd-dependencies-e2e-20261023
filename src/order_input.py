"""Validate order lines and return immutable, deterministic tuples."""
import re


def _validate_integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('Expected an integer within the allowed bounds')


def normalize_items(value: object) -> tuple:
    if not isinstance(value, list) or not 1 <= len(value) <= 100:
        raise ValueError('Expected between 1 and 100 order lines')
    result = []
    seen = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {'sku', 'quantity', 'unit_cents'}:
            raise ValueError('Order line fields must be sku, quantity and unit_cents')
        sku, quantity, price = item['sku'], item['quantity'], item['unit_cents']
        if not isinstance(sku, str) or re.fullmatch(r'[A-Z][A-Z0-9-]{0,15}', sku) is None or sku in seen:
            raise ValueError('Expected a unique uppercase ASCII SKU')
        _validate_integer(quantity, 1, 100)
        _validate_integer(price, 0, 1000000)
        seen.add(sku)
        result.append((sku, quantity, price))
    return tuple(result)
