import copy
import unittest

from src.order_total import subtotal
from tests.test_order_input import line
from tests.order_oracle_support import rejects_mutant


class OrderTotalFunctionalTests(unittest.TestCase):
    def test_multiplies_quantity(self):
        self.assertEqual(subtotal([line()]), 250)

    def test_sums_lines(self):
        self.assertEqual(subtotal([line(), line('B', 1, 300)]), 550)

    def test_zero_price(self):
        self.assertEqual(subtotal([line(unit_cents=0)]), 0)

    def test_integer_arithmetic(self):
        self.assertEqual(subtotal([line(quantity=3, unit_cents=101)]), 303)
        self.assertIs(type(subtotal([line()])), int)

    def test_upper_bounds(self):
        value = [line('A' + str(i), 100, 1000000) for i in range(100)]
        self.assertEqual(subtotal(value), 10000000000)

    def test_preserves_input(self):
        value = [line()]
        old = copy.deepcopy(value)
        subtotal(value)
        self.assertEqual(value, old)

    def test_rejects_invalid_input(self):
        for value in ([], [line(quantity=True)], [line(unit_cents=-1)], [line(), line()]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                subtotal(value)


class OrderTotalAdversarialTests(unittest.TestCase):
    def test_rejects_zero(self):
        rejects_mutant(self, 'src/order_total.py', 'subtotal',
                       'def subtotal(items):\n    return 0',
                       'tests.test_order_total.OrderTotalFunctionalTests')

    def test_rejects_ignored_quantity(self):
        rejects_mutant(self, 'src/order_total.py', 'subtotal',
                       'def subtotal(items):\n    return sum(price for _, qty, price in normalize_items(items))',
                       'tests.test_order_total.OrderTotalFunctionalTests')


if __name__ == '__main__':
    unittest.main()
