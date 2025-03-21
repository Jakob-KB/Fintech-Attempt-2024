import numpy as np
import pandas as pd

# For reproducibility (remove or change the seed for different results)
np.random.seed(42)

# Set the number of days and starting price (the last price in your sample is 100.0)
num_days = 365
start_day = 365
end_day = start_day + num_days - 1
start_price = 100.0

# Generate daily changes with a normal distribution (mean=0, std=0.5)
# You can adjust the standard deviation to simulate different volatility levels.
daily_changes = np.random.normal(loc=0, scale=0.5, size=num_days)

# Create a price series as a random walk.
prices = [start_price]
for change in daily_changes:
    new_price = prices[-1] + change
    prices.append(new_price)

# Remove the first element (the starting price is at day 364 in your dataset)
prices = prices[1:]

# Create a DataFrame with days and prices.
days = np.arange(start_day, end_day + 1)
df = pd.DataFrame({"Day": days, "Price": prices})

# Save to CSV
df.to_csv("synthetic_data.csv", index=False)
print("CSV file 'synthetic_data.csv' has been generated.")
