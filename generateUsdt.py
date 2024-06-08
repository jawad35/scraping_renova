import random
from datetime import datetime, timedelta

# Get today's date
start_date = datetime.today()

# Generate 30 entries
entries = []
for i in range(30):
    # Generate random high and low prices
    high = random.randint(68900, 69100)
    low = random.randint(67900, 68100)
    if low > high:
        low, high = high, low  # Swap if low is greater than high
    
    # Determine close price, with a higher chance of being closer to the high for green lines,
    # and closer to the low for red lines
    close = random.randint(low, high)
    if close > (high + low) / 2:
        close = random.randint((high + close) // 2, high)
    else:
        close = random.randint(low, (low + close) // 2)
    
    # Increment date by 1 day for each entry
    date = start_date + timedelta(days=i)
    
    # Append entry to the list
    entries.append(f"{{ open: {low}, high: {high}, low: {low}, close: {close}, time: '{date.strftime('%Y-%m-%d')}' }}")

# Print the generated entries separated by commas
print(', '.join(entries))
