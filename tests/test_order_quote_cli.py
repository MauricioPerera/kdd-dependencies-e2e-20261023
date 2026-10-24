import copy
import json
import unittest

from src.quote_cli import quote
from tests.test_order_input import line
from tests.order_oracle_support import run_cli, rejects_mutant


class OrderQuoteFunctionalTests(unittest.TestCase):
    def test_composes_total_and_shipping(self):
        self.assertEqual(quote([line(), line('B', 1, 300)]),
                         dict(subtotal_cents=550, shipping_cents=400, total_cents=950))

    def test_free_shipping(self):
        self.assertEqual(quote([line(quantity=6)]),
                         dict(subtotal_cents=750, shipping_cents=0, total_cents=750))

    def test_zero_price_still_pays_shipping(self):
        self.assertEqual(quote([line(quantity=1, unit_cents=0)]),
                         dict(subtotal_cents=0, shipping_cents=250, total_cents=250))

    def test_preserves_input(self):
        value = [line()]
        old = copy.deepcopy(value)
        quote(value)
        self.assertEqual(value, old)

    def test_rejects_invalid(self):
        for value in (None, [], [line(quantity=True)], [line(), line()]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                quote(value)


class OrderQuoteAdversarialTests(unittest.TestCase):
    def test_rejects_fixed_quote(self):
        rejects_mutant(self, 'src/quote_cli.py', 'quote',
                       "def quote(items):\n    return dict(subtotal_cents=0, shipping_cents=0, total_cents=0)",
                       'tests.test_order_quote_cli.OrderQuoteFunctionalTests')

    def test_rejects_missing_shipping_in_total(self):
        rejects_mutant(self, 'src/quote_cli.py', 'quote',
                       "def quote(items):\n    value = subtotal(items)\n    return dict(subtotal_cents=value, shipping_cents=shipping(items), total_cents=value)",
                       'tests.test_order_quote_cli.OrderQuoteFunctionalTests')


class OrderQuoteCliTests(unittest.TestCase):
    def assert_bad_input(self, payload):
        code, out, err = run_cli(payload)
        self.assertEqual(code, 2)
        self.assertEqual(out, '')
        self.assertTrue(err.startswith('Error:'), err)
        self.assertNotIn('Traceback', err)

    def test_real_pipeline(self):
        code, out, err = run_cli(json.dumps([line(), line('B', 1, 300)]))
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out), dict(subtotal_cents=550, shipping_cents=400, total_cents=950))
        self.assertEqual(len(out.splitlines()), 1)

    def test_free_shipping(self):
        code, out, err = run_cli(json.dumps([line(quantity=6)]))
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out), dict(subtotal_cents=750, shipping_cents=0, total_cents=750))

    def test_external_whitespace(self):
        code, out, err = run_cli('\n  ' + json.dumps([line()]) + ' \n')
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out), dict(subtotal_cents=250, shipping_cents=325, total_cents=575))

    def test_empty_input(self):
        self.assert_bad_input('')

    def test_malformed_json(self):
        self.assert_bad_input('[')

    def test_invalid_root(self):
        self.assert_bad_input('null')

    def test_invalid_data(self):
        self.assert_bad_input(json.dumps([line(quantity=True)]))

    def test_duplicate_sku(self):
        self.assert_bad_input(json.dumps([line(), line()]))

    def test_invalid_unicode_sku(self):
        self.assert_bad_input(json.dumps([line('ÁRBOL')], ensure_ascii=False))

    def test_invalid_utf8(self):
        self.assert_bad_input(b'\xff')

    def test_extra_json_document(self):
        self.assert_bad_input('[]\n[]')

    def test_help(self):
        code, out, err = run_cli('', '--help')
        self.assertEqual((code, err), (0, ''))
        self.assertIn('usage:', out.lower())

    def test_unknown_argument(self):
        code, out, err = run_cli('[]', '--unknown')
        self.assertEqual((code, out), (2, ''))
        self.assertIn('error', err.lower())
        self.assertNotIn('Traceback', err)


if __name__ == '__main__':
    unittest.main()
