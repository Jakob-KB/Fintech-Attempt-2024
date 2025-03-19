import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from indicators import compute_SMA  # Example: using compute_SMA; you can import others as needed.


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
                # Round xdata to nearest whole day.
                day_clicked = int(round(event.xdata))
                # Find the nearest day from the DataFrame.
                nearest_day = df['Day'].iloc[(df['Day'] - day_clicked).abs().argmin()]
                price_clicked = df.loc[df['Day'] == nearest_day, 'Price'].values[0]
                annot.xy = (nearest_day, price_clicked)
                annot.set_text(f"Day: {nearest_day}\nPrice: {price_clicked:.2f}")
                annot.set_visible(True)
                fig.canvas.draw_idle()

        def on_mouse_release(event):
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
    # Read CSV file into a DataFrame; expecting columns "Day" and "Price"
    df = pd.read_csv(file_path)
    # Compute daily returns for further analysis.
    df['Return'] = df['Price'].pct_change()

    plotter = InstrumentPlotter(df)
    # Add core plot features.
    plotter.add_feature(PriceLineFeature())
    plotter.add_feature(CrosshairCursorFeature())
    plotter.add_feature(ClickAnnotationFeature())

    # Add a 14-day SMA indicator using our new API.
    plotter.add_indicator(
        indicator_func=compute_SMA,
        indicator_params={'window': 14},
        chart_params={'color': 'blue', 'linestyle': '--'},
        label="14-Day SMA"
    )
    plotter.add_indicator(
        indicator_func=compute_SMA,
        indicator_params={'window': 28},
        chart_params={'color': 'red', 'linestyle': '-.'},
        label="28-Day SMA"
    )

    # Display summary statistics.
    plotter.display_statistics()
    # Create and show the plot.
    plotter.create_plot()


if __name__ == '__main__':
    # Change the file path as needed.
    view_instrument("./data/historic_data/Fintech Token_price_history.csv")
