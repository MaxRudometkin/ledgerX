import datetime
import requests
from exchange_api.consts import (BASE_URL, API_VERSION, DATE_FORMAT, DATE_LATEST, DATE_ENDPOINT, CCY_ENDPOINT,
                                 EMPTY_CCY_ENDPOINT, MAX_CACHE_SIZE, DECIMALS)


class ExchangeApi:
    def __init__(self):
        """
        Initialize the cache, set the maximum cache size, last request timestamp, and rate limit.
        """
        self.cache = {}
        self.max_cache_size = MAX_CACHE_SIZE
        self.last_request_ts = None
        self.rate_limit_sec = 1
        self.__update_cache()

    def __update_cache(self, date: str = None) -> None:
        """
        Update the cache with the response from the send_request method for the given date.

        :param date(string): The date for which the request is made. Defaults to None.
        :return: None
        """
        response = self.__send_request(date, 'usd')
        self.cache[response['date']] = response

        # clear cache
        if len(self.cache) > self.max_cache_size:
            min_date = min(self.cache.keys())
            del self.cache[min_date]

    def __send_request(self, date: str = None, ccy: str = None) -> dict:
        """
        Send a request with optional date and currency parameters and return the JSON response.

        :param date: Optional date parameter in string format.
        :param ccy: Optional currency parameter in string format.
        :return: Dictionary containing the JSON response from the request.
        """
        self.__check_rate_limit()
        url = self.__build_url(date, ccy)
        try:
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            # todo: handle http error
            raise Exception('Current date is unavailable. Try different date.', err)
        except requests.exceptions.ConnectionError as err:
            # todo: handle http error
            raise Exception(err)
        except requests.exceptions.Timeout as err:
            # todo: handle http error
            raise Exception(err)
        except requests.exceptions.RequestException as err:
            # todo: handle http error
            raise Exception(err)

    def __check_rate_limit(self) -> None:
        """
        Check if the rate limit has been reached before making a request.

        Returns:
            None
        """
        now = datetime.datetime.now().timestamp()
        if self.last_request_ts and (now - self.last_request_ts) > self.rate_limit_sec:
            raise Exception(f'Too many requests. Rate limit is {self.rate_limit_sec} request per second.')

    def __validate_input(self, base: str, quote: str, amount: float, date: str) -> tuple:
        """
        Validates the input parameters for base currency, quote currency, amount, and date.

        Args:
            base (str): The base currency.
            quote (str): The quote currency.
            amount (float): The amount of currency.
            date (str): The date for currency conversion.

        Returns:
            tuple: A tuple containing base_usd, counter_usd, and amount.
        """
        # check date
        if date in [None, 'latest']:
            date = max(self.cache.keys())
        else:
            self.__is_valid_date(date)
            if date not in self.cache:
                self.__update_cache(date)

        # check base currency
        base_usd = self.cache[date]['usd'].get(base)
        if not base_usd:
            raise Exception(f'Unsupported BASE currency("{base}"). Try different currency')

        # check quote currency
        counter_usd = self.cache[date]['usd'].get(quote)
        if not counter_usd:
            raise Exception(f'Unsupported QUOTE currency("{quote}"). Try different currency')

        # check amount
        try:
            amount = float(amount)
        except ValueError:
            raise Exception(f'Unsupported AMOUNT type ("{amount}"). Must be a number')

        return base_usd, counter_usd, amount

    @staticmethod
    def __build_url(date: str = None, ccy: str = None) -> str:
        """
        Build a URL based on the given date and currency parameters.

        Args:
            date (str, optional): The date for the URL. Defaults to None.
            ccy (str, optional): The currency code for the URL. Defaults to None.

        Returns:
            str: The constructed URL.
        """
        date = DATE_LATEST if date is None else date
        date_endpoint = DATE_ENDPOINT.format(date)
        ccy_endpoint = EMPTY_CCY_ENDPOINT if ccy is None else CCY_ENDPOINT.format(ccy)
        return BASE_URL + date_endpoint + API_VERSION + ccy_endpoint

    @staticmethod
    def __is_valid_date(date_string: str) -> None:

        try:
            datetime.datetime.strptime(date_string, DATE_FORMAT)
        except ValueError:
            raise Exception(f'Wrong date format. Date must be in {DATE_FORMAT} format.')

    def __convert(self, base: str, quote: str, amount: float, date: str = None) -> dict:
        """
        Convert the given amount from one currency to another based on the provided exchange rates.

        Parameters:
            base (str): The base currency symbol.
            quote (str): The quote currency symbol.
            amount (float): The amount to be converted.
            date (str, optional): The date for which the exchange rate should be used. Defaults to None.

        Returns:
            dict: A dictionary containing the converted amount, exchange rate, base currency, and quote currency.
        """
        base_usd, counter_usd, amount = self.__validate_input(base, quote, amount, date)
        base_total_usd = amount / base_usd

        converted_amount = base_total_usd * counter_usd
        converted_amount = round(converted_amount, DECIMALS)

        rate = base_total_usd / converted_amount
        rate = round(rate, DECIMALS)

        return {
            'converted_amount': converted_amount,
            'rate': rate,
            'base': base,
            'quote': quote
        }

    def convert(self, base: str, quote: str, amount: float, date=None) -> dict:
        """
        A method to convert the given amount from one currency to another.

        Args:
            base (str): The base currency to convert from.
            quote (str): The currency to convert to.
            amount (float): The amount to convert.
            date (str, optional): The date of exchange rate to use for conversion.

        Returns:
            dict: If successful, returns a dictionary with the converted amount.
                  If unsuccessful, returns a dictionary with an 'error' key containing the error message.
        """
        try:
            return self.__convert(base, quote, amount, date)
        except Exception as err:
            return {'error': str(err)}
