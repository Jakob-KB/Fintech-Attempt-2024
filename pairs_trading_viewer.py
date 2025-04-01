import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

# Load CSV files for each stock
milk = pd.read_csv("data/seen_data/Milk_price_history.csv")
coffee = pd.read_csv("data/seen_data/Coffee_price_history.csv")

# Normalize the prices so that the first day is set to 100
milk['Normalized'] = milk['Price'] / milk['Price'].iloc[0] * 100
coffee['Normalized'] = coffee['Price'] / coffee['Price'].iloc[0] * 100

# Create the plot and axis
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(milk['Day'], milk['Normalized'], linestyle='-', color="blue", label='Milk')
ax.plot(coffee['Day'], coffee['Normalized'], linestyle='-', color="green", label='Coffee')
ax.set_title('Normalized Price Comparison: Milk vs Coffee by Day')
ax.set_xlabel('Day')
ax.set_ylabel('Normalized Price (Base 100)')
ax.legend()
ax.grid(True)

# Add an interactive crosshair cursor to the plot
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

plt.show()
