from utils import CoinPaprikApi, create_parser

if __name__ == '__main__':
    parser, args = create_parser()

    data = CoinPaprikApi(args.start_date, args.end_date, args.coin)

    if args.average_price_by_month:
        for month, value in data.get_average().items():
            print(f'{month} | {value}')
    elif args.consecutive_increase:
        date_from, date_to, diff = data.consecutive_increase()
        print(f"Longest consecutive increase in value was from {date_from} to {date_to} with increase of {diff}$")
    elif args.export:
        data.data_export(file_name=args.file, format_choice=args.format)
