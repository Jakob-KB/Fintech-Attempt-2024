import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from indicators import compute_SMA
from simulation import TradingEngine
from tools import average_price_over_last_X_days


# Base class for all plot features.
class PlotFeature:
    def apply(self, fig, ax, df):
        raise NotImplementedError("Each feature must implement an apply method.")


# Feature to plot the price line.
class PriceLineFeature(PlotFeature):
    def __init__(self, label='Price', color='black'):
        self.label = label
        self.color = color

    def apply(self, fig, ax, df):
        ax.plot(df['Day'], df['Price'], label=self.label, color=self.color)
        ax.set_xlabel("Day")
        ax.set_ylabel("Price")
        ax.legend()


# Feature to add a crosshair cursor.
class CrosshairCursorFeature(PlotFeature):
    def __init__(self, color='red', linewidth=1):
        self.color = color
        self.linewidth = linewidth
        self.cursor = None  # Store a reference to the cursor

    def apply(self, fig, ax, df):
        # Store the Cursor instance in an attribute so it isn't garbage-collected.
        self.cursor = Cursor(ax, useblit=True, color=self.color, linewidth=self.linewidth)


# Feature to add interactive annotation on mouse click.
class ClickAnnotationFeature(PlotFeature):
    def __init__(self, offset=(20, 20)):
        self.offset = offset

    def apply(self, fig, ax, df):
        annot = ax.annotate("", xy=(0, 0), xytext=self.offset,
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def on_mouse_press(event):
            if event.inaxes == ax and event.button == 1:
                # Retrieve the click coordinates in display space.
                click_x, click_y = event.x, event.y

                # Convert the DataFrame's data points to display coordinates.
                data_points = np.column_stack((df['Day'], df['Price']))
                disp_coords = ax.transData.transform(data_points)

                # Compute Euclidean distance in display coordinates.
                distances = np.linalg.norm(disp_coords - np.array([click_x, click_y]), axis=1)
                idx_min = distances.argmin()

                # Get the nearest point from the DataFrame.
                nearest_day = df.iloc[idx_min]['Day']
                nearest_price = df.iloc[idx_min]['Price']

                # Update the annotation with the nearest point's values.
                annot.xy = (nearest_day, nearest_price)
                annot.set_text(f"Day: {nearest_day}\nPrice: {nearest_price:.2f}")
                annot.set_visible(True)
                fig.canvas.draw_idle()

        def on_mouse_release(event):
            annot.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("button_press_event", on_mouse_press)
        fig.canvas.mpl_connect("button_release_event", on_mouse_release)


# Feature to add an indicator to the plot.
class IndicatorFeature(PlotFeature):
    def __init__(self, indicator_func, indicator_params=None, chart_params=None, label="Indicator"):
        """
        indicator_func: Function that accepts a DataFrame and additional indicator parameters.
        indicator_params: Dictionary of parameters for the indicator function.
        chart_params: Dictionary of matplotlib plot parameters (e.g., color, linestyle).
        label: Label for the indicator.
        """
        self.indicator_func = indicator_func
        self.indicator_params = indicator_params if indicator_params is not None else {}
        self.chart_params = chart_params if chart_params is not None else {}
        self.label = label

    def apply(self, fig, ax, df):
        # Compute the indicator values.
        indicator_series = self.indicator_func(df, **self.indicator_params)
        # Plot the indicator.
        ax.plot(df['Day'], indicator_series, label=self.label, **self.chart_params)
        ax.legend()


# Main plotter class that uses a list of features.
class InstrumentPlotter:
    def __init__(self, df):
        self.df = df
        self.features = []

    def add_feature(self, feature: PlotFeature):
        self.features.append(feature)

    def add_indicator(self, indicator_func, indicator_params=None, chart_params=None, label="Indicator"):
        """
        A helper method to add an indicator feature using indicator parameters and chart styling.
        """
        self.add_feature(IndicatorFeature(indicator_func, indicator_params, chart_params, label))

    def compute_statistics(self):
        stats = {
            'median_price': self.df['Price'].median(),
            'mean_price': self.df['Price'].mean(),
            'max_price': self.df['Price'].max(),
            'min_price': self.df['Price'].min(),
            'std_price': self.df['Price'].std()
        }
        return stats

    def display_statistics(self):
        stats = self.compute_statistics()
        print(f"Median Price: {stats['median_price']:.2f}")
        print(f"Mean Price: {stats['mean_price']:.2f}")
        print(f"Max Price: {stats['max_price']:.2f}")
        print(f"Min Price: {stats['min_price']:.2f}")
        print(f"Standard Deviation: {stats['std_price']:.2f}")

    def create_plot(self, title="Instrument Price", figsize=(14, 7)):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(title)
        # Apply all features.
        for feature in self.features:
            feature.apply(fig, ax, self.df)
        plt.tight_layout()
        plt.show()


def view_instrument(file_path):
    # Read CSV file into a DataFrame; expecting columns "Day" and "Price".
    df = pd.read_csv(file_path)
    # Compute daily returns for further analysis.
    df['Return'] = df['Price'].pct_change()
    # Create a 'Day' column if not already present (e.g., use the DataFrame's index).
    if 'Day' not in df.columns:
        df['Day'] = df.index

    plotter = InstrumentPlotter(df)
    # Add core plot features.
    plotter.add_feature(PriceLineFeature())
    plotter.add_feature(CrosshairCursorFeature())
    plotter.add_feature(ClickAnnotationFeature())
    # Optionally, add an indicator

    # Display summary statistics.
    plotter.display_statistics()
    # Create and show the plot.
    plotter.create_plot(title="Instrument Price and Trades Performance")


if __name__ == '__main__':
    # Change the file path as needed.
    #view_instrument("./data/LLM_data/UQ Dollar_price_history.csv")
    view_instrument("./synthetic_data.csv")
