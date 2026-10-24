import copy
import unittest

from src.order_input import normalize_items
from tests.order_oracle_support import rejects_mutant


def line(sku='A-1', quantity=2, unit_cents=125):
    return dict(sku=sku, quantity=quantity, unit_cents=unit_cents)


class OrderInputFunctionalTests(unittest.TestCase):
    def test_normalized_tuple(self):
        self.assertEqual(normalize_items([line()]), (('A-1', 2, 125),))

    def test_preserves_order(self):
        self.assertEqual(normalize_items([line('B', 1, 300), line('A')]),
                         (('B', 1, 300), ('A', 2, 125)))

    def test_does_not_mutate(self):
        value = [line()]
        original = copy.deepcopy(value)
        normalize_items(value)
        self.assertEqual(value, original)

    def test_boundaries(self):
        self.assertEqual(normalize_items([line('A123456789012345', 100, 1000000)]),
                         (('A123456789012345', 100, 1000000),))
        self.assertEqual(normalize_items([line('A', 1, 0)]), (('A', 1, 0),))

    def test_one_hundred_lines(self):
        value = [line('A' + str(i), 1, i) for i in range(100)]
        self.assertEqual(normalize_items(value), tuple((x['sku'], 1, x['unit_cents']) for x in value))

    def test_root_types(self):
        for value in (None, {}, (), 'abc', 1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_items(value)

    def test_empty_or_too_many(self):
        for value in ([], [line('A' + str(i)) for i in range(101)]):
            with self.subTest(size=len(value)), self.assertRaises(ValueError):
                normalize_items(value)

    def test_line_types(self):
        for value in (None, [], 'A', 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_items([value])

    def test_exact_fields(self):
        for value in ({'sku': 'A'}, dict(line(), extra=1)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_items([value])

    def test_invalid_sku(self):
        for sku in ('', 'a', ' A', 'A ', '1A', 'A_1', 'A\n', 'ÁRBOL', 'A' * 17, 1, None):
            with self.subTest(sku=sku), self.assertRaises(ValueError):
                normalize_items([line(sku)])

    def test_duplicate_sku(self):
        with self.assertRaises(ValueError):
            normalize_items([line(), line()])

    def test_invalid_quantities(self):
        for quantity in (0, -1, 101, True, False, 2.0, '2', None):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                normalize_items([line(quantity=quantity)])

    def test_invalid_prices(self):
        for price in (-1, 1000001, True, 1.5, '100', None):
            with self.subTest(price=price), self.assertRaises(ValueError):
                normalize_items([line(unit_cents=price)])


class OrderInputAdversarialTests(unittest.TestCase):
    def test_rejects_identity(self):
        rejects_mutant(self, 'src/order_input.py', 'normalize_items',
                       'def normalize_items(value):\n    return value',
                       'tests.test_order_input.OrderInputFunctionalTests')

    def test_rejects_empty_constant(self):
        rejects_mutant(self, 'src/order_input.py', 'normalize_items',
                       'def normalize_items(value):\n    return ()',
                       'tests.test_order_input.OrderInputFunctionalTests')


if __name__ == '__main__':
    unittest.main()
