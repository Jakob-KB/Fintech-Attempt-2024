import pandas as pd

# Define the file path
filepath = "./data/historic_data/UQ Dollar_price_history.csv"

# Load the data
data = pd.read_csv(filepath)

# Count the number of times the price goes above 101
count_above_101 = (data['Price'] > 101).sum()

# Print the result
print(f"The price goes above 101 {count_above_101} times.")
