import requests
import json
import pandas as pd
import datetime as dt

# Prompt the user for the frequency
frequency = input("Please enter the frequency (1m/5m/30m/.../1h/6h/1d/): ")

def get_bars(symbol, interval):
    root_url = 'https://api.binance.com/api/v1/klines'
    url = f'{root_url}?symbol={symbol}&interval={interval}'
    print(url)
    data = json.loads(requests.get(url).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                  'open', 'high', 'low', 'close', 'volume',
                  'close_time', 'quote_asset_volume', 'number_of_trades',
                  'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df['time'] = [dt.datetime.fromtimestamp(x / 1000.0).isoformat() for x in df.open_time]
    df = df[['open', 'high', 'low', 'close', 'time']]
    df.index = pd.to_datetime(df['time'])
    return df

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def csv_to_json(csv_filename, json_filename):
    df = pd.read_csv(csv_filename)
    json_data = df.to_json(orient='records', date_format='iso')
    with open(json_filename, 'w') as json_file:
        json_file.write(json_data)
    print(f'Data saved to {json_filename}')

# Main function
def main():
    symbol = 'BTCUSDT'
    interval = frequency

    df = get_bars(symbol, interval)
    csv_filename = '_btcusdt.csv'
    json_filename = '_btcusdt.json'

    if not df.empty:
        save_to_csv(df, csv_filename)
        csv_to_json(csv_filename, json_filename)

if __name__ == "__main__":
    main()
