# ProfilSoftwareRecrTask
Recruitmnent task for ProfiSoftware Internship

# Usage

To see help and usage in console:
```
python3 script.py -h
or
python3 script.py
```
Show average monthly prices for selected coin in a given time period
```
-average-price-by-month
-avg 

Use example:

python3 script.py -average-price-by-month --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin
python3 script.py -avg --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin
```


Show longest consecutive price increase in given time period
```
-consecutive-increase
-incr

Use example:

python3 script.py -consecutive-increase --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin
python3 script.py -incr --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin
```


Export prices data to json or csv file
```
-export
-exp

Use example:

python3 script.py -export --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin --format=csv --file=my_file.csv
python3 script.py -exp --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin --format=csv --file=my_file.csv
```

Required arguments for file export:
```
--format=csv
or
--format=json
default is csv if not provided

--file=name_of_file.csv
defaults to '(coin_name)_data .(format)' if not provided
Required arguments:
```

```
--start-date=yyyy-mm-dd or yyyy-mm
--end-date=yyyy-mm-dd or yyyy-mm
if not provided user will be asked for input,
if day is not specified, defaults to first day of month for start date and last day of month for end date
```
Optional:
```
--coin=eth-ethereum
default is btc-bitcoin,
```
full list of available coins: https://api.coinpaprika.com/v1/coins



