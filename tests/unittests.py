import unittest
from unittest.mock import patch
from server_soap.server_soap import CurrencyConverterService, is_valid_api_key

VALID_API_KEY = 'apikey1'
INVALID_API_KEY = 'abc'


class TestCurrencyConverterService(unittest.TestCase):

    def setUp(self):
        self.service = CurrencyConverterService()

    @patch('server_soap.server_soap.fetch_currency_rates', return_value={'EUR': 0.85, 'USD': 1.0})  # replace the fetch_currency_rates function so that it returns fixed values
    def test_convert_valid(self, mock_fetch_currency_rates):
        result = self.service.convert(None, VALID_API_KEY, 'USD', 'EUR', 100)
        self.assertEqual(result, 85)
        mock_fetch_currency_rates.assert_called_once()  # the fetch_currency_rates must be called once otherwise fail

    def test_convert_same_currency(self):
        result = self.service.convert(None, VALID_API_KEY, 'USD', 'USD', 100)
        self.assertEqual(result, 100)

    def test_convert_invalid_currency_code(self):
        with self.assertRaises(ValueError):
            self.service.convert(None, VALID_API_KEY, 'INVALID', 'EUR', 100)

        with self.assertRaises(ValueError):
            self.service.convert(None, VALID_API_KEY, 'USD', 'INVALID', 100)

    def test_convert_invalid_api_key(self):
        with self.assertRaises(ValueError):
            self.service.convert(None, INVALID_API_KEY, 'USD', 'EUR', '100')

    def test_is_valid_api_key(self):
        self.assertTrue(is_valid_api_key(VALID_API_KEY))
        self.assertFalse(is_valid_api_key(INVALID_API_KEY))


if __name__ == '__main__':
    unittest.main()

