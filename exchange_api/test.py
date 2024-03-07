import unittest
import time
import random
from exchange_api.main_api import ExchangeApi

test_instance = ExchangeApi()


# class TestCurrencyConverter(unittest.TestCase):
#
#     def setUp(self):
#         # Set up any required resources for the tests
#         pass
#
#     def tearDown(self):
#         # Clean up any resources used for the tests
#         pass
#
#     def test_convert_valid_amount(self):
#         # Test converting from one currency to another with a valid amount and exchange rate
#         # Implement test code here
#         pass
#
#     def test_convert_invalid_amount(self):
#         # Test converting from one currency to another with an invalid amount
#         # Implement test code here
#         pass
#
#     def test_convert_specific_date(self):
#         # Test converting from one currency to another with a valid amount and a specific date for exchange rate
#         # Implement test code here
#         pass


def random_data_test():
    """
    Perform a series of random tests using the test_instance cache.
    Select random dates, currency pairs, and amounts to test the convert method and print the results.
    """
    max_date = max(test_instance.cache.keys())
    dates = [None, 'latest', '2024-03-02', '2023-03-02', '2024-03-024', '2022-03-02', '2023-04-02', '2024-13-024',
             '2024-03-22']

    for n, _ in enumerate(range(10)):
        time.sleep(random.random())
        from_currency = random.choice(list(test_instance.cache[max_date]['usd'].keys()))
        to_currency = random.choice(list(test_instance.cache[max_date]['usd'].keys()) + ['laksjdh', '7doiu'])
        amount = random.randrange(0, 500)
        date = random.choice(dates)
        print(f'---Test #:{n}:\n ({date}) Convert {amount} {from_currency} to {to_currency}:')
        print(test_instance.convert(from_currency, to_currency, amount, date))


if __name__ == '__main__':
    # unittest.main()
    random_data_test()
