import argparse
import csv
from datetime import datetime, timedelta
import json
import requests


def get_response(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('ERROR')
    return response.json()


def create_parser():
    """
    Function wraps parser object creation
    and adds required arguments
    :return: parser and args objects
    """
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('-average-price-by-month', '-avg', help='average_price', action="store_true")
    parser_.add_argument('-consecutive-increase', '-incr',  help='cons_incr', action="store_true")
    parser_.add_argument('-export', '-exp', help='exp', action="store_true")
    parser_.add_argument('--start-date', '--sdate',  help='start_date')
    parser_.add_argument('--end-date', '--edate',  help='start_date')
    parser_.add_argument('--format', '--f',  help='format')
    parser_.add_argument('--file', help='file')

    args_ = parser_.parse_args()

    return parser_, args_


class CurrencyData:
    def __init__(self, start_date, end_date):
        self.start_date, self.end_date = self.check_date(start_date, end_date)

    def __str__(self):
        return f'CoinPaprika Api bitcoin data handler for period from {self.start_date} to {self.end_date}'

    @staticmethod
    def check_date(start, end):
        try:
            if len(start) == 7 and len(end) == 7:
                start_date_parsed = datetime(int(start[:4]), int(start[5:]), 1).date()
                end_date_parsed = datetime(int(end[:4]) + int(end[5:]) // 12, int(end[5:]) % 12 + 1, 1).date() - timedelta(days=1)
            elif len(start) == 10 and len(end) == 10:
                start_date_parsed = datetime.strptime(start, '%Y-%m-%d').date()
                end_date_parsed = datetime.strptime(end, '%Y-%m-%d').date()
            else:
                raise ValueError('Date has incorrect format')
            if start_date_parsed > end_date_parsed:
                print('Start date cannot be before end date')
                raise ValueError
        except ValueError:
            print('Date has incorrect format, please provide date in a yyyy-mm-dd format, or yyyy-mm')
            start = input('Starting date: ')
            end = input('Ending date: ')
            start_date_parsed, end_date_parsed = CurrencyData.check_date(start, end)
        if end_date_parsed > datetime.now().date():
            print('End date cannot be in the future, please invent time travel first.')
            print('End date set for today')
            end_date_parsed = datetime.now().date()
        return start_date_parsed, end_date_parsed

    def get_average(self):
        start = datetime(self.start_date.year, self.start_date.month, 1).date()
        end = datetime(self.end_date.year + self.end_date.month // 12, self.end_date.month % 12 + 1, 1).date() - timedelta(days=1)
        print(f'Fetching average monthly prices for period from {start.year}-{start.month} to {end.year}-{end.month} please wait...')
        averages_for_months = {}
        while True:
            end_date_helper = datetime(start.year + start.month // 12, start.month % 12 + 1, 1).date() - timedelta(days=1)
            url = f'https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start={start}&end={end_date_helper}'
            month_values = [val['close'] for val in get_response(url)]
            if month_values:
                averages_for_months[f"{start.strftime('%Y-%m')}"] = round(sum(month_values) / len(month_values), 2)
            else:
                averages_for_months[f"{start.strftime('%Y-%m')}"] = 'No data for this month'
            start = end_date_helper + timedelta(days=1)
            if end_date_helper == end:
                break
        for month, value in averages_for_months.items():
            print(f'{month} | {value}')

        return averages_for_months  # dict of 'month' : avg_value

    def consecutive_increase(self):
        url = f'https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start={self.start_date}&end={self.end_date}'
        data = get_response(url)
        arr = [val['close'] if val['close'] else 0 for val in data]
        if arr == []:
            print('No data for given period')
            return None
        i = 0
        counter = 0
        data_list = []
        while i < len(arr):
            if arr[i] <= arr[i + 1]:
                counter += 1
            else:
                data_list.append((i, counter,))
                counter = 1
            i += 1
            if i + 1 == len(arr):
                data_list.append((i, counter,))
                break

        longest_sequence = sorted(list(data_list), key=lambda values: values[1], reverse=True)[0]
        sequence_start_index = longest_sequence[0] - longest_sequence[1] + 1
        sequence_end_index = longest_sequence[0]
        diff = round(arr[sequence_end_index] - arr[sequence_start_index], 2)

        date_from = data[sequence_start_index]['time_open'][:10]
        date_to = data[sequence_end_index]['time_open'][:10]
        print(f"Longest consecutive increase in value was from {date_from} to {date_to} with increase of {diff}$")
        return arr[sequence_start_index:sequence_end_index] #array with increasing values sequence

    def data_export(self, format_choice, file_name):
        url = f'https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start={self.start_date}&end={self.end_date}'
        data = get_response(url)
        if format_choice == 'csv':

            with open(file_name, mode='w') as csv_file:
                export_writer = csv.writer(csv_file, delimiter=',')
                export_writer.writerow(['Date', 'Price'])
                for d in data:
                    date = d['time_open'][:10]
                    price = round(d['close'], 2)
                    export_writer.writerow([date, price])
                print('Data succesfully imported to CSV file')

        elif format_choice == 'json':
            with open(file_name, mode='w') as json_file:
                json_data_list = []
                for d in data:
                    date = d['time_open'][:10]
                    price = round(d['close'], 2)
                    json_data = {
                        'date': date,
                        'price': price
                    }
                    json_data_list.append(json_data)
                json.dump(json_data_list, json_file, indent=4)
                print('Data succesfully imported to JSON file')


if __name__ == '__main__':
    parser, args = create_parser()

    data = CurrencyData(args.start_date, args.end_date)

    if args.average_price_by_month:
        data.get_average()
    elif args.consecutive_increase:
        data.consecutive_increase()
    elif args.export:
        data.data_export(format_choice=args.format, file_name=args.file)
