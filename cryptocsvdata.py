import csv
import json
from datetime import datetime

# Define the path to your CSV file and the output JSON file
csv_file_path = '_btcusdt.csv'
json_file_path = 'historical_data.json'

# Read the CSV file
with open(csv_file_path, newline='') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    historical_data = []

    for row in csv_reader:
        historical_data.append({
            "open": float(row["o"]),
            "high": float(row["h"]),
            "low": float(row["l"]),
            "close": float(row["c"]),
            "time": datetime.utcfromtimestamp(int(row["open_time"]) / 1000).strftime('%Y-%m-%dT%H:%M:%S')
        })

# Convert the list to JSON format
historical_data_json = json.dumps(historical_data, indent=2)

# Write the JSON data to a file
with open(json_file_path, 'w') as jsonfile:
    jsonfile.write(historical_data_json)

print(f"Data has been written to {json_file_path}")
