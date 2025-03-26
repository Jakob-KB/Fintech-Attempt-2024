import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


class ChartView:
    def __init__(self, price_data: list[float]):
        self.price_data = price_data

        # Each series is stored with its target plot ("main" or "relative")
        self.data_series = {}  # name -> (data: list[float], plot: str)
        self.marker_series = {}  # name -> (data: list[float or None], plot: str)
        self.data_styles = {}  # name -> dict(style)
        self.marker_styles = {}  # name -> dict(style)

    def add_data_series(self, name: str, data: list[float], style_dict=None, plot: str = "main"):
        self.data_series[name] = (data, plot)
        self.data_styles[name] = style_dict or {}

    def add_marker_series(self, name: str, data: list[float | None], style_dict=None, plot: str = "main"):
        self.marker_series[name] = (data, plot)
        self.marker_styles[name] = style_dict or {}

    def view(self, title="Instrument Price", cursor_color='red',
             cursor_linewidth=1, annotation_offset=(20, 20)):
        # Separate series by the specified plot designation.
        main_series = {name: data for name, (data, plot) in self.data_series.items() if plot == "main"}
        relative_series = {name: data for name, (data, plot) in self.data_series.items() if plot == "relative"}

        main_markers = {name: data for name, (data, plot) in self.marker_series.items() if plot == "main"}
        relative_markers = {name: data for name, (data, plot) in self.marker_series.items() if plot == "relative"}

        # Check if any relative data exists.
        if relative_series or relative_markers:
            fig, (ax_main, ax_rel) = plt.subplots(
                nrows=2, sharex=True,
                gridspec_kw={'height_ratios': [3, 1]},
                figsize=(14, 7)
            )
        else:
            fig, ax_main = plt.subplots(figsize=(14, 7))
            ax_rel = None

        ax_main.set_title(title)
        ax_main.set_xlabel("Day")
        ax_main.set_ylabel("Price")

        # Plot main series on the main axis.
        for name, values in main_series.items():
            ax_main.plot(range(len(values)), values, label=name, **self.data_styles.get(name, {}))
        for name, values in main_markers.items():
            x_vals = [i for i, v in enumerate(values) if v is not None]
            y_vals = [v for v in values if v is not None]
            ax_main.scatter(x_vals, y_vals, label=name, **self.marker_styles.get(name, {}))
        ax_main.legend()

        # Plot relative series on the relative axis.
        if ax_rel is not None:
            ax_rel.set_xlabel("Day")
            ax_rel.set_ylabel("Indicator")
            for name, values in relative_series.items():
                ax_rel.plot(range(len(values)), values, label=name, **self.data_styles.get(name, {}))
            for name, values in relative_markers.items():
                x_vals = [i for i, v in enumerate(values) if v is not None]
                y_vals = [v for v in values if v is not None]
                ax_rel.scatter(x_vals, y_vals, label=name, **self.marker_styles.get(name, {}))
            ax_rel.legend()
            ax_rel.grid(True)

        # Crosshair for the main axis.
        Cursor(ax_main, useblit=True, color=cursor_color, linewidth=cursor_linewidth)

        # Annotation on click for the main axis.
        annot = ax_main.annotate("", xy=(0, 0), xytext=annotation_offset,
                                 textcoords="offset points",
                                 bbox=dict(boxstyle="round", fc="w"),
                                 arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def on_mouse_press(event):
            if event.inaxes != ax_main or event.button != 1:
                return
            click_x, click_y = event.x, event.y
            data_points = np.column_stack((range(len(self.price_data)), self.price_data))
            disp_coords = ax_main.transData.transform(data_points)
            distances = np.linalg.norm(disp_coords - np.array([click_x, click_y]), axis=1)
            idx = distances.argmin()
            nearest_day = idx
            nearest_price = self.price_data[idx]
            annot.xy = (nearest_day, nearest_price)
            annot.set_text(f"Day: {nearest_day}\nPrice: {nearest_price:.2f}")
            annot.set_visible(True)
            fig.canvas.draw_idle()

        def on_mouse_release(event):
            annot.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("button_press_event", on_mouse_press)
        fig.canvas.mpl_connect("button_release_event", on_mouse_release)

        plt.tight_layout()
        plt.show()


def sma_indicator(prices: list[float], window: int) -> list[float]:
    # Pre-fill the initial values with None where we don't have enough data to calculate the SMA.
    sma_list = [None] * (window - 1)
    for i in range(window - 1, len(prices)):
        window_prices = prices[i - window + 1:i + 1]
        sma_list.append(sum(window_prices) / window)
    return sma_list


def ema_indicator(prices: list[float], window: int) -> list[float]:
    ema_list = [None] * (window - 1)
    alpha = 2 / (window + 1)
    initial_sma = sum(prices[:window]) / window
    ema_list.append(initial_sma)
    ema_prev = initial_sma
    for price in prices[window:]:
        ema_current = (price - ema_prev) * alpha + ema_prev
        ema_list.append(ema_current)
        ema_prev = ema_current
    return ema_list


def rsi_indicator(prices: list[float], window: int) -> list[float]:
    rsi_list = [None] * window
    gains = []
    losses = []
    for i in range(1, window + 1):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    rsi_list.append(rsi)
    for i in range(window + 1, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(change, 0)
        loss = max(-change, 0)
        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_list.append(rsi)
    return rsi_list


def macd_indicator(prices: list[float],
                   short_window: int = 12,
                   long_window: int = 26,
                   signal_window: int = 9) -> tuple[list[float], list[float], list[float]]:
    """
    Compute the MACD line, Signal line, and Histogram using exponential moving averages.
    """
    # Using pandas for simplicity
    price_series = pd.Series(prices)
    ema_short = price_series.ewm(span=short_window, adjust=False).mean()
    ema_long = price_series.ewm(span=long_window, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line.tolist(), signal_line.tolist(), histogram.tolist()


def bollinger_bands(prices: list[float],
                    window: int,
                    num_std: float = 2
                    ) -> tuple[list[float], list[float], list[float]]:
    price_series = pd.Series(prices)
    sma = price_series.rolling(window).mean()
    std = price_series.rolling(window).std()
    upper_band = sma + num_std * std
    lower_band = sma - num_std * std
    return sma.tolist(), upper_band.tolist(), lower_band.tolist()


def main():
    """
    - Main plot is for looking at price history and indicators that are important relevant to the price.

    - Relative plot is for looking at indicators that don't necessarily scale to the price like
    RSI or other similar ratio based indicators.

    """
    # Read price history to a dataframe
    df = pd.read_csv("data/unseen_data/Fun Drink_price_history.csv")

    # Convert the prices to a list
    prices = df["Price"].tolist()

    # Calculate any indicators we may want to view/use
    sma = sma_indicator(prices, 28)
    ema = ema_indicator(prices, 7)
    macd_line, macd_signal, macd_hist = macd_indicator(prices)
    bb_middle, bb_upper, bb_lower = bollinger_bands(prices, window=14, num_std=1)

    # Create a chart with the price data
    chart = ChartView(prices)

    # Add indicators to the main plot
    chart.add_data_series("Price", prices, {"color": "black"}, plot="main")
    chart.add_data_series("EMA (3 Days)", ema, {"color": "red"}, plot="main")
    # chart.add_data_series("Bollinger Upper (20 Days)", bb_upper, {"color": "red"}, plot="main")
    # chart.add_data_series("Bollinger Lower (20 Days)", bb_lower, {"color": "green"}, plot="main")
    # chart.add_data_series("Bollinger Middle (20 Days)", bb_middle, {"color": "blue"}, plot="main")

    # Add indicators to the relative plot
    chart.add_data_series("EMA (3 Days)", ema, {"color": "red"}, plot="main")
    # chart.add_data_series("MACD Line", macd_line, {"color": "orange"}, plot="relative")
    # chart.add_data_series("MACD Signal", macd_signal, {"color": "magenta"}, plot="relative")
    # chart.add_data_series("MACD Histogram", macd_hist, {"color": "grey"}, plot="relative")

    # !!!!!!!!!!!!! If you try to uncomment and see the MACD data you probably wont be able to as its
    # in the range lik -0.5 to 0.5 in this case while the RSI is obviously in range 0 to 100 !!!!!!!!

    # Lastly create and view the chart
    chart.view("Instrument Chart")


if __name__ == '__main__':
    main()
