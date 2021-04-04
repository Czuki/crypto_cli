from utils import CoinPaprikApi, create_parser

if __name__ == '__main__':
    parser, args = create_parser()

    if any([args.average_price_by_month, args.consecutive_increase, args.export]):
        coin_data = CoinPaprikApi(args.start_date, args.end_date, args.coin)
        if args.average_price_by_month:
            for month, value in coin_data.get_average().items():
                print(f'{month} | {value}')
        elif args.consecutive_increase:
            date_from, date_to, diff = coin_data.consecutive_increase()
            print(f"Longest consecutive increase in value for {coin_data.coin}"
                  f" was from {date_from} to {date_to} with increase of {diff}$")
        elif args.export:
            coin_data.data_export(file_name=args.file, format_choice=args.format)
    else:
        parser.print_help()