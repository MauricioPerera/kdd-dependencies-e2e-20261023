"""Compose a deterministic order quote and expose it as a JSON CLI."""
import argparse
import json
import sys

from .order_total import subtotal
from .order_shipping import shipping


def quote(items: object) -> dict:
    value = subtotal(items)
    freight = shipping(items)
    return dict(subtotal_cents=value, shipping_cents=freight, total_cents=value + freight)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Quote an order from JSON UTF-8 on stdin.')
    parser.parse_args(argv)
    try:
        items = json.loads(sys.stdin.buffer.read().decode('utf-8'))
        result = quote(items)
    except ValueError:
        print('Error: invalid order input', file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
