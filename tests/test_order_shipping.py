import copy
import unittest

from src.order_shipping import shipping
from tests.test_order_input import line
from tests.order_oracle_support import rejects_mutant


class OrderShippingFunctionalTests(unittest.TestCase):
    def test_one_to_five_units(self):
        for quantity, expected in ((1, 250), (2, 325), (3, 400), (4, 475), (5, 550)):
            with self.subTest(quantity=quantity):
                self.assertEqual(shipping([line(quantity=quantity)]), expected)

    def test_six_units_free(self):
        self.assertEqual(shipping([line(quantity=6)]), 0)

    def test_many_units_free(self):
        self.assertEqual(shipping([line(quantity=100)]), 0)

    def test_combines_quantities(self):
        self.assertEqual(shipping([line(quantity=2), line('B', 3)]), 550)
        self.assertEqual(shipping([line(quantity=3), line('B', 3)]), 0)

    def test_price_does_not_affect_shipping(self):
        self.assertEqual(shipping([line(quantity=1, unit_cents=1000000)]), 250)
        self.assertEqual(shipping([line(quantity=6, unit_cents=0)]), 0)

    def test_integer_result(self):
        self.assertIs(type(shipping([line()])), int)

    def test_preserves_input(self):
        value = [line()]
        old = copy.deepcopy(value)
        shipping(value)
        self.assertEqual(value, old)

    def test_rejects_invalid(self):
        for value in ([], [line(quantity=0)], [line(), line()]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                shipping(value)


class OrderShippingAdversarialTests(unittest.TestCase):
    def test_rejects_always_free(self):
        rejects_mutant(self, 'src/order_shipping.py', 'shipping',
                       'def shipping(items):\n    return 0',
                       'tests.test_order_shipping.OrderShippingFunctionalTests')

    def test_rejects_flat_fee(self):
        rejects_mutant(self, 'src/order_shipping.py', 'shipping',
                       'def shipping(items):\n    return 250',
                       'tests.test_order_shipping.OrderShippingFunctionalTests')


if __name__ == '__main__':
    unittest.main()
