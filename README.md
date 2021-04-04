# ProfilSoftwareRecrTask
Recruitmnent task for ProfiSoftware Internship

# Usage

To see help and usage in console:
```
python3 script.py -h
or
python3 script.py
```
```
-average-price-by-month
-avg 
```
Shows average monthly prices for selected coin in a given time period
Use example:
```
python3 script.py -average-price-by-month --start-date=2020-10-10 --end-date=2020-12-12 --coin=btc-bitcoin
```
```
-consecutive-increase
-incr
```

```
-export
-exp
```

Required arguments:
```
--start-date=yyyy-mm-dd or yyyy-mm
--end-date=yyyy-mm-dd or yyyy-mm
```
if not provided user will be asked for input,
if day is not specified, defaults to first day of month for start date and last day of month for end date

Optional:
```
--coin=eth-ethereum
```
default is btc-bitcoin,
full list of available coins: https://api.coinpaprika.com/v1/coins

```
-export
-exp
```
Required arguments for file export:
```
--format=csv
or
--format=json
```
default is csv if not provided

```
--file=name_of_file.csv
```
defaults to '(coin_name)_data .(format)' if not provided

