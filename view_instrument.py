import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

from indicators import *

def view_instrument(file_path):
    # Read CSV file into a DataFrame; expecting columns "Day" and "Price"
    df = pd.read_csv(file_path)

    # Compute summary statistics.
    median_price = df['Price'].median()
    mean_price = df['Price'].mean()
    max_price = df['Price'].max()
    min_price = df['Price'].min()
    std_price = df['Price'].std()

    # Compute daily returns and volatility.
    df['Return'] = df['Price'].pct_change()
    volatility = df['Return'].std()

    print(f"Median Price: {median_price:.2f}")
    print(f"Mean Price: {mean_price:.2f}")
    print(f"Max Price: {max_price:.2f}")
    print(f"Min Price: {min_price:.2f}")
    print(f"Standard Deviation: {std_price:.2f}")
    print(f"Volatility (Std of Returns): {volatility:.2f}")

    # Create the plot.
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df['Day'], df['Price'], label='Price', color='black')

    ax.set_title("Instrument Price")
    ax.set_xlabel("Day")
    ax.set_ylabel("Price")
    ax.legend()
    plt.tight_layout()

    # Add a crosshair cursor.
    cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

    # Create an annotation to display the current Day and Price.
    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def on_mouse_press(event):
        if event.inaxes == ax and event.button == 1:
            # Round xdata to nearest whole day.
            day_clicked = int(round(event.xdata))
            # Find the nearest day from the DataFrame (in case the CSV days are not perfectly sequential)
            nearest_day = df['Day'].iloc[(df['Day'] - day_clicked).abs().argmin()]
            # Get the corresponding price for that day.
            price_clicked = df.loc[df['Day'] == nearest_day, 'Price'].values[0]
            annot.xy = (nearest_day, price_clicked)
            annot.set_text(f"Day: {nearest_day}\nPrice: {price_clicked:.2f}")
            annot.set_visible(True)
            fig.canvas.draw_idle()

    def on_mouse_release(event):
        # annot.set_visible(False)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_mouse_press)
    fig.canvas.mpl_connect("button_release_event", on_mouse_release)

    plt.show()

if __name__ == '__main__':
    # Change the file path as needed.
    view_instrument("./data/historic_data/UQ Dollar_price_history.csv")
