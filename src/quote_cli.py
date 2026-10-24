"""Approved interfaces; implementation belongs to TASK-004."""
from .order_total import subtotal
from .order_shipping import shipping

def quote(items: object) -> dict:
    raise NotImplementedError("TASK-004 pending")

def main(argv=None) -> int:
    raise NotImplementedError("TASK-004 pending")

if __name__ == "__main__":
    raise SystemExit(main())
