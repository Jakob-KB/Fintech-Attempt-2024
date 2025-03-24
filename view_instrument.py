import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from utils.tools import sma_indicator


class ChartView:
    def __init__(self, price_data: list[float]):
        self.price_data = price_data

        self.data_series = {}    # name -> list[float]
        self.marker_series = {}  # name -> list[float or None]
        self.data_styles = {}    # name -> dict(style)
        self.marker_styles = {}  # name -> dict(style)

    def add_data_series(self, name: str, data: list[float], style_dict=None):
        self.data_series[name] = data
        self.data_styles[name] = style_dict or {}

    def add_marker_series(self, name: str, data: list[float | None], style_dict=None):
        self.marker_series[name] = data
        self.marker_styles[name] = style_dict or {}

    def create_plot(self, title="Instrument Price", price_color='black',
                    cursor_color='red', cursor_linewidth=1, annotation_offset=(20, 20)):

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.set_title(title)
        ax.set_xlabel("Day")
        ax.set_ylabel("Price")

        # Plot regular time series
        for name, values in self.data_series.items():
            ax.plot(range(len(values)), values, label=name, **self.data_styles.get(name, {}))

        # Plot markers (skipping None)
        for name, values in self.marker_series.items():
            x_vals = [i for i, v in enumerate(values) if v is not None]
            y_vals = [v for v in values if v is not None]
            ax.scatter(x_vals, y_vals, label=name, **self.marker_styles.get(name, {}))

        ax.legend()

        # Crosshair
        Cursor(ax, useblit=True, color=cursor_color, linewidth=cursor_linewidth)

        # Annotation on click
        annot = ax.annotate("", xy=(0, 0), xytext=annotation_offset,
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def on_mouse_press(event):
            if event.inaxes != ax or event.button != 1:
                return

            click_x, click_y = event.x, event.y
            data_points = np.column_stack((range(len(self.price_data)), self.price_data))
            disp_coords = ax.transData.transform(data_points)
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

def get_trades(stock):
    from algorithm import Algorithm
    from simulation import TradingEngine

    engine = TradingEngine()


def main():
    df = pd.read_csv("data/historic_data/UQ Dollar_price_history.csv")
    prices = df["Price"].tolist()

    sma = sma_indicator(prices, 28)

    chart = ChartView(prices)
    chart.add_data_series("Price", prices, {"color": "black"})
    chart.add_data_series("SMA (28 Days)", sma, {"color": "red", "linestyle": "--"})
    chart.create_plot("UQ Dollar Price History")


if __name__ == '__main__':
    main()
