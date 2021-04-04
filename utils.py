import argparse
import csv
from datetime import datetime, timedelta
import json
import requests_cache
import requests


def get_response(url):
    """
    Connects to API with provided url
    and returns data in json format
    raises exception if request fails
    uses request_cache to store fetched data
    :param url: external API url
    :return: response.json object
    """
    response = requests.get(url)
    requests_cache.install_cache(cache_name='coin_cache', backend='sqlite', expire_after=180)
    if response.status_code != 200:
        print(response.status_code)
        return None
    return response.json()


def create_parser():
    """
    creates parser object and adds required command line arguments
    :return: parser and args objects
    """
    parser = argparse.ArgumentParser(description='Coinpaprika api coin data parser')
    parser.add_argument('-average-price-by-month', '-avg', help='average_price', action="store_true")
    parser.add_argument('-consecutive-increase', '-incr', help='cons_incr', action="store_true")
    parser.add_argument('-export', '-exp', help='exp', action="store_true")
    parser.add_argument('--start-date', '--sdate', help='start_date')
    parser.add_argument('--end-date', '--edate', help='start_date')
    parser.add_argument('--format', '--f', help='format')
    parser.add_argument('--file', help='file')
    parser.add_argument('--coin', help='coin')

    args = parser.parse_args()

    return parser, args


class CoinPaprikApi:

    def __init__(self, coin, start_date, end_date):
        self.coin = coin \
            if requests.get(f'https://api.coinpaprika.com/v1/coins/{coin}').status_code == 200 else 'btc-bitcoin'
        self.start_date, self.end_date = self.check_date(start_date, end_date)
        self.response_data = self.get_response_data(self.start_date, self.end_date, self.coin)

    def __str__(self):
        return f'CoinPaprika Api {self.coin} data handler for period from {self.start_date} to {self.end_date}'

    @staticmethod
    def get_response_data(start, end, coin):
        """
        gets all response data for provided time period
        :param start: str starting date 'yyyy-mm-dd' or 'yyyy-mm'
        :param end: str ending date 'yyyy-mm-dd' or 'yyyy-mm'
        :param coin: str type of coin
        :return: response_data
        """
        start_date = start
        days_diff = (end - start).days  # total days to process, API has max limit of 1 year
        response_data = []
        while True:
            limit = 366 if days_diff > 366 else days_diff
            url = f'https://api.coinpaprika.com/v1/coins/{coin}/ohlcv/historical?start={start_date}&limit={limit}'
            response_data = response_data + get_response(url)
            start_date = start_date + timedelta(days=limit)
            days_diff = days_diff - limit
            if start_date >= end:
                break
        return response_data

    @staticmethod
    def check_date(start, end):
        """
        Converts date to datetime format and validates the date
        if date is incorrect user will be asked to provide correct date
        if date is yyyy-mm we fix it to yyyy-mm-dd,
        start_date day will be set to first day of a month and end_date day to last day of a month
        :param start: str starting date 'yyyy-mm-dd' or 'yyyy-mm'
        :param end: str ending date 'yyyy-mm-dd' or 'yyyy-mm'
        :return: start_date: datetime.date object yyyy-mm-dd
                 end_date: datetime.date object yyyy-mm-dd
        """
        start = '' if start is None else start
        end = '' if end is None else end

        try:
            if len(start) == 7 and len(end) == 7:
                start_year = int(start[:4])
                start_month = int(start[5:])
                end_year = int(end[:4]) + int(end[5:]) // 12
                end_month = int(end[5:]) % 12 + 1
                start_date = datetime(start_year, start_month, 1).date()
                end_date = datetime(end_year, end_month, 1).date() - timedelta(days=1)
            elif len(start) == 10 and len(end) == 10:
                start_date = datetime.strptime(start, '%Y-%m-%d').date()
                end_date = datetime.strptime(end, '%Y-%m-%d').date()
            else:
                raise ValueError('Date has incorrect format')

            if start_date > end_date or end_date > datetime.now().date() or start_date > datetime.now().date():
                raise ValueError

        except ValueError:
            print('Date has incorrect value, format or points to date in the future,'
                  ' please provide correct date in a yyyy-mm-dd or yyyy-mm format')
            start = input('Starting date: ')
            end = input('Ending date: ')
            start_date, end_date = CoinPaprikApi.check_date(start, end)

        return start_date, end_date

    def get_average(self):
        """
        calculates average monthly prices of selected coin
        for provided time period, minimal time period is 1 month
        if date is provided with specific days,
        start_date day is set to first day of month
        end_date day is set to last day of month
        :return: averages_for_months: dict {'yyyy-mm': average monthly price}
        """
        start = datetime(self.start_date.year, self.start_date.month, 1).date()
        end_year = self.end_date.year + self.end_date.month // 12
        end_month = self.end_date.month % 12 + 1
        end = datetime(end_year, end_month, 1).date() - timedelta(days=1)

        print(f"Fetching average monthly prices for {self.coin}, "
              f"period from {start.strftime('%Y-%m')} to {end.strftime('%Y-%m')}")
        print(f'Please wait...')
        averages_for_months = {}
        while True:
            # set end_date day to last day of month
            helper_year = start.year + start.month // 12
            helper_month = start.month % 12 + 1
            end_helper = datetime(helper_year, helper_month, 1).date() - timedelta(days=1)

            url = f'https://api.coinpaprika.com/v1/coins/{self.coin}/ohlcv/historical?start={start}&end={end_helper}'
            month_values = [val['close'] for val in get_response(url)]
            if month_values:
                averages_for_months[f"{start.strftime('%Y-%m')}"] = round(sum(month_values) / len(month_values), 2)
            else:
                averages_for_months[f"{start.strftime('%Y-%m')}"] = 'No data for this month'
            start = end_helper + timedelta(days=1)
            if end_helper == end:
                break
        return averages_for_months

    def consecutive_increase(self):
        """
        finds longest consecutive period when price of coin was increasing
        :return: date_from: datetime.date object
                date_to: datetime.date object
                diff: price difference
        """

        prices = [round(data['close'], 2) for data in self.response_data]

        i = 0
        counter = 0
        data_list = []
        while i < len(prices):
            if prices[i] <= prices[i + 1]:
                counter += 1
            else:
                data_list.append((i, counter,))
                counter = 1
            i += 1
            if i + 1 == len(prices):
                data_list.append((i, counter,))
                break

        longest_sequence = sorted(data_list, key=lambda values: values[1], reverse=True)[0]
        sequence_start_index = longest_sequence[0] - longest_sequence[1] + 1
        sequence_end_index = longest_sequence[0]
        diff = round(prices[sequence_end_index] - prices[sequence_start_index], 2)
        date_from = self.response_data[sequence_start_index]['time_close'][:10]
        date_to = self.response_data[sequence_end_index]['time_close'][:10]

        return date_from, date_to, diff

    def data_export(self, file_name, format_choice):
        """
        :param format_choice: string
        :param file_name: string
        :return: creates file and prints message
        """

        format_choice = 'csv' if not format_choice else format_choice
        file_name = f'{self.coin}_data.{format_choice}' if not file_name else file_name

        if format_choice == 'csv':
            with open(file_name, mode='w') as csv_file:
                export_writer = csv.writer(csv_file, delimiter=',')
                export_writer.writerow(['Date', 'Price'])
                for data in self.response_data:
                    date = data['time_open'][:10]
                    price = round(data['close'], 2)
                    export_writer.writerow([date, price])
                print('Data successfully exported to CSV file')

        elif format_choice == 'json':
            with open(file_name, mode='w') as json_file:
                json_data_list = []
                for data in self.response_data:
                    date = data['time_open'][:10]
                    price = round(data['close'], 2)
                    json_data = {
                        'date': date,
                        'price': price
                    }
                    json_data_list.append(json_data)
                json.dump(json_data_list, json_file, indent=4)
                print('Data successfully exported to JSON file')
