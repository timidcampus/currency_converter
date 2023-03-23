import unittest
from unittest.mock import patch
from server.server import CurrencyConverterService


class TestCurrencyConverterService(unittest.TestCase):

    def setUp(self):
        self.service = CurrencyConverterService()

    @patch('server.server.fetch_currency_rates', return_value={'EUR': 0.85, 'USD': 1.0})  # replace the fetch_currency_rates function so that it returns fixed values
    def test_convert_valid(self, mock_fetch_currency_rates):
        result = self.service.convert(None, 'USD', 'EUR', 100)
        self.assertEqual(result, 85)
        mock_fetch_currency_rates.assert_called_once()  # the fetch_currency_rates must be called once otherwise fail

    def test_convert_same_currency(self):
        result = self.service.convert(None, 'USD', 'USD', 100)
        self.assertEqual(result, 100)

    def test_convert_invalid_currency_code(self):
        with self.assertRaises(ValueError):
            self.service.convert(None, 'INVALID', 'EUR', 100)

        with self.assertRaises(ValueError):
            self.service.convert(None, 'USD', 'INVALID', 100)


if __name__ == '__main__':
    unittest.main()