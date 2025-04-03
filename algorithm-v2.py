from utils.tools import ema_indicator, sma_indicator, bollinger_bands, rsi_indicator, rsi_series, macd_indicator
from trading_classes import Trade, UQDollarStrategy  # imported trading classes

def strictly_increasing(price_history: list, days: int) -> bool:
    if len(price_history) < days:
        return False
    subset = price_history[-days:]
    return all(earlier < later for earlier, later in zip(subset, subset[1:]))

def strictly_decreasing(price_history: list, days: int) -> bool:
    if len(price_history) < days:
        return False
    subset = price_history[-days:]
    return all(earlier > later for earlier, later in zip(subset, subset[1:]))

# Centralized default configuration
DEFAULT_CONFIG = {
    "UQ Dollar": {
        "lower_bound": 100,
        "upper_bound": 100,
    },
    "Fintech Token": {
        "sma_short_days": 7,
        "sma_long_days": 28,
        "difference_threshold": 10,
    },
    "Fun Drink": {
        "ema_window": 3,       # number of days to compute the EMA
        "trade_size": 10000,   # incremental trade unit
    },
}

class Algorithm:
    def __init__(self, positions, config: dict = {}):
        # Actual price history updated during trading; starts empty.
        self.data = {
            "Fintech Token": [],
            "Fun Drink": [],
            "Red Pens": [],
            "Thrifted Jeans": [],
            "UQ Dollar": [],
            "Coffee": [],
            "Coffee Beans": [],
            "Goober Eats": [],
            "Milk": []
        }
        self.position_limits = {
            "Fintech Token": 35,
            "Fun Drink": 10000,
            "Red Pens": 40000,
            "Thrifted Jeans": 400,
            "UQ Dollar": 650,
            "Coffee": 30000,
            "Coffee Beans": 200,
            "Goober Eats": 75000,
            "Milk": 2500
        }
        self.instruments = [
            "Fintech Token",
            "Fun Drink",
            "Red Pens",
            "Thrifted Jeans",
            "UQ Dollar",
            "Coffee",
            "Coffee Beans",
            "Goober Eats",
            "Milk",
        ]
        # Preloaded historical data (e.g., last 28 days) for padding
        self.preload_data = {
            'Coffee': [3.45, 3.48, 3.47, 3.48, 3.45, 3.5, 3.46, 3.5, 3.53, 3.5, 3.54, 3.53, 3.53, 3.55, 3.53, 3.56, 3.53, 3.54, 3.53, 3.54, 3.56, 3.55, 3.56, 3.6, 3.6, 3.57, 3.56, 3.59],
            'Coffee Beans': [127.93, 124.0, 127.55, 126.11, 125.04, 126.62, 126.93, 128.42, 126.83, 126.67, 126.53, 127.42, 128.39, 126.69, 127.61, 125.83, 128.43, 127.0, 126.0, 129.62, 130.02, 128.59, 131.54, 131.68, 129.59, 132.82, 129.9, 130.21],
            'Fintech Token': [1063.48, 1048.2, 1065.09, 1057.47, 1058.85, 1052.55, 1070.01, 1037.92, 1055.31, 1064.08, 1064.62, 1047.38, 1059.54, 1028.18, 1004.84, 973.44, 942.79, 907.36, 911.1, 880.76, 834.53, 838.99, 859.16, 823.74, 848.96, 870.13, 846.91, 854.4],
            'Fun Drink': [7.95, 7.47, 7.46, 8.58, 8.17, 7.8, 8.16, 7.8, 7.93, 8.24, 8.35, 7.75, 8.18, 8.03, 7.79, 7.52, 7.97, 7.9, 7.63, 7.64, 7.71, 7.59, 7.72, 8.17, 8.94, 8.63, 7.71, 8.02],
            'Goober Eats': [1.48, 1.51, 1.5, 1.52, 1.47, 1.51, 1.46, 1.48, 1.48, 1.46, 1.5, 1.48, 1.48, 1.49, 1.51, 1.49, 1.45, 1.48, 1.46, 1.49, 1.47, 1.51, 1.47, 1.51, 1.5, 1.47, 1.53, 1.53],
            'Milk': [5.96, 6.01, 5.89, 5.84, 6.15, 5.86, 6.12, 6.29, 6.18, 6.4, 6.36, 6.33, 6.28, 6.31, 6.37, 6.29, 6.32, 6.34, 6.44, 6.33, 6.31, 6.35, 6.4, 6.46, 6.36, 6.13, 6.37, 6.31],
            'Red Pens': [2.21, 2.19, 2.19, 2.19, 2.2, 2.2, 2.21, 2.22, 2.18, 2.2, 2.2, 2.2, 2.2, 2.19, 2.2, 2.2, 2.19, 2.2, 2.2, 2.2, 2.2, 2.18, 2.18, 2.2, 2.21, 2.2, 2.2, 2.2],
            'Thrifted Jeans': [75.79, 79.35, 68.25, 80.42, 76.57, 69.61, 70.62, 72.99, 71.17, 81.45, 72.92, 73.78, 67.88, 67.47, 63.88, 73.67, 71.29, 68.88, 61.5, 64.03, 66.34, 71.66, 65.82, 71.27, 74.61, 63.9, 75.64, 68.61],
            'UQ Dollar': [100.0, 98.64, 100.2, 100.38, 100.08, 100.0, 99.82, 99.79, 98.49, 100.55, 99.78, 100.0, 100.36, 101.13, 100.68, 99.89, 100.27, 100.23, 100.0, 99.82, 98.86, 99.91, 99.82, 100.72, 99.85, 100.0, 100.08, 100.0]
        }
        self.day = 0  # Current trading day
        self.positions = positions  # Current positions (e.g. {"UQ Dollar": 650, ...})
        self.daily_spending = {}  # Daily spending by instrument
        self.trades = {}  # (Optional) For logging closed trades
        self.config = DEFAULT_CONFIG.copy()
        for key, params in config.items():
            if key in self.config and isinstance(params, dict):
                self.config[key].update(params)
            else:
                self.config[key] = params

        # Instantiate the UQ Dollar strategy with its trade size and exit condition.
        # (This strategy will handle opening/closing trades for UQ Dollar.)
        self.uq_dollar_strategy = UQDollarStrategy(self, trade_size=650, exit_condition=100)

    def get_recent_history(self, instrument: str, days: int) -> list:
        """
        Returns the most recent 'days' worth of data for the instrument.
        If actual data is insufficient, it pads the result with preloaded data.
        """
        actual = self.data.get(instrument, [])
        if len(actual) >= days:
            return actual[-days:]
        else:
            needed = days - len(actual)
            preload = self.preload_data.get(instrument, [])
            return preload[-needed:] + actual

    def get_current_price(self, instrument):
        """
        Use the most recent actual price if available; otherwise, fall back to preloaded data.
        """
        if self.data.get(instrument):
            return self.data[instrument][-1]
        else:
            return self.preload_data[instrument][-1]

    def get_positions(self):
        """
        Determine desired positions for each instrument.
        For UQ Dollar, use the UQDollarStrategy class to manage the trade.
        Returns a dictionary of desired positions.
        """
        current_positions = self.positions
        desired_positions = {instr: 0 for instr in self.position_limits}

        # Use the UQ Dollar strategy to evaluate and update the trade for UQ Dollar.
        uq_summary = self.uq_dollar_strategy.evaluate()
        # The performance summary from UQDollarStrategy includes the current position.
        desired_positions["UQ Dollar"] = uq_summary["position"]

        # (Optionally, add similar calls for other instruments/trading functions here.)

        # Update daily spending as the total absolute value of desired positions.
        total_spending = 0
        for instr in self.instruments:
            total_spending += abs(desired_positions[instr] * self.get_current_price(instr))
        self.daily_spending[self.day] = total_spending

        # On the final day (day 364), calculate and print the average exit prices.
        if self.day == 364:
            self.final_trade_summary("UQ Dollar")

        return desired_positions

    def final_trade_summary(self, asset):
        """
        On the final day, compute the average exit price for closed long and short trades for a given asset,
        and calculate the average accuracy between the expected value (EV) and realised value (RV)
        for all closed trades.
        """
        closed_trades = self.trades.get(asset, [])
        long_trades = [trade for trade in closed_trades if trade.position > 0 and trade.exit_price is not None]
        short_trades = [trade for trade in closed_trades if trade.position < 0 and trade.exit_price is not None]

        avg_long_exit = sum(trade.exit_price for trade in long_trades) / len(long_trades) if long_trades else None
        avg_short_exit = sum(trade.exit_price for trade in short_trades) / len(short_trades) if short_trades else None

        # Calculate EV accuracy for each closed trade
        ev_accuracies = []
        for trade in closed_trades:
            if trade.realised_value is not None:
                # Use the strategy's exit condition for EV calculation
                ev = trade.calculate_expected_value(self.uq_dollar_strategy.exit_condition)
                rv = trade.realised_value
                if rv != 0:
                    percentage_error = abs(ev - rv) / abs(rv) * 100
                    accuracy = 100 - percentage_error
                else:
                    # If RV is zero, set accuracy to 100 if EV is also zero.
                    accuracy = 100 if ev == 0 else 0
                ev_accuracies.append(accuracy)
        avg_accuracy = sum(ev_accuracies) / len(ev_accuracies) if ev_accuracies else None

        print(f"Final Summary for {asset} trades on day {self.day}:")
        if avg_long_exit is not None:
            print(f"Average long trade exit price: {avg_long_exit}")
        else:
            print("No closed long trades.")
        if avg_short_exit is not None:
            print(f"Average short trade exit price: {avg_short_exit}")
        else:
            print("No closed short trades.")
        if avg_accuracy is not None:
            print(f"Average EV Accuracy for {asset} trades: {avg_accuracy:.2f}%")
        else:
            print("No closed trades for EV Accuracy calculation.")

        return {"avg_long_exit": avg_long_exit, "avg_short_exit": avg_short_exit, "avg_accuracy": avg_accuracy}

