from utils.tools import ema_indicator, sma_indicator, bollinger_bands, rsi_indicator, rsi_series, macd_indicator

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
        self.positions = positions  # Current positions
        self.daily_spending = {}  # Daily spending by instrument
        self.trades = {}
        self.config = DEFAULT_CONFIG.copy()
        for key, params in config.items():
            if key in self.config and isinstance(params, dict):
                self.config[key].update(params)
            else:
                self.config[key] = params

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
        # Use the most recent actual price if available; otherwise, fall back to preloaded data.
        if self.data.get(instrument):
            return self.data[instrument][-1]
        else:
            return self.preload_data[instrument][-1]

    def get_positions(self):
        total_budget = 500_000  # Maximum absolute value of positions allowed per day
        current_positions = self.positions
        position_limits = self.position_limits

        # Initialise desired positions for all instruments.
        desired_positions = {instr: 0 for instr in position_limits}

        # Trading function for UQ Dollar (no indicator needed)
        def trade_uq_dollar():
            asset = "UQ Dollar"
            current_price = self.get_current_price(asset)
            if current_price < 100:
                desired_positions[asset] = position_limits[asset]
            elif current_price > 100:
                desired_positions[asset] = -position_limits[asset]
            else:
                desired_positions[asset] = current_positions.get(asset, 0)

        # Trading function for Fintech Token using SMA indicators (with padded data)
        def trade_fintech_token():
            asset = "Fintech Token"
            params = self.config["Fintech Token"]
            padded_short = self.get_recent_history(asset, params["sma_short_days"])
            padded_long = self.get_recent_history(asset, params["sma_long_days"])
            sma_short = sma_indicator(padded_short, params["sma_short_days"])
            sma_long = sma_indicator(padded_long, params["sma_long_days"])
            difference = abs(sma_short - sma_long)
            if self.day > 2:
                if sma_short > sma_long and difference > params["difference_threshold"]:
                    desired_positions[asset] = position_limits[asset]
                elif sma_short < sma_long and difference > params["difference_threshold"]:
                    desired_positions[asset] = -position_limits[asset]
                else:
                    desired_positions[asset] = position_limits[asset]

        # Trading function for Fun Drink using EMA with padded data.
        def trade_fun_drink():
            asset = "Fun Drink"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            params = self.config["Fun Drink"]
            ema_window = params["ema_window"]
            padded_history = self.get_recent_history(asset, ema_window)
            ema = ema_indicator(padded_history, ema_window)
            if current_price < ema:
                desired_positions[asset] = position_limits[asset]
            elif current_price > ema:
                desired_positions[asset] = -position_limits[asset]
            else:
                desired_positions[asset] = current_position

        # Trading function for Goober Eats using EMA with padded data.
        def trade_goober_eats():
            asset = "Goober Eats"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            ema_window = 7
            padded_history = self.get_recent_history(asset, ema_window)
            ema = ema_indicator(padded_history, ema_window)
            threshold = 0.0025
            if current_price < ema - threshold:
                desired_positions[asset] = position_limits[asset]
            elif current_price > ema + threshold:
                desired_positions[asset] = -position_limits[asset]
            else:
                desired_positions[asset] = current_position

        # Trading function for Thrifted Jeans using EMA with padded data.
        def trade_thrifted_jeans():
            asset = "Thrifted Jeans"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            ema_window = 5
            padded_history = self.get_recent_history(asset, ema_window)
            ema = ema_indicator(padded_history, ema_window)
            if current_price < ema:
                desired_positions[asset] = position_limits[asset]
            elif current_price > ema:
                desired_positions[asset] = -position_limits[asset]
            else:
                desired_positions[asset] = current_position

        # Trading function for Coffee using EMA with padded data.
        def trade_coffee_simple():
            asset = "Coffee"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            ema_window = 3
            padded_history = self.get_recent_history(asset, ema_window)
            ema = ema_indicator(padded_history, ema_window)
            if current_price < ema:
                desired_positions[asset] = position_limits[asset]
            elif current_price > ema:
                desired_positions[asset] = -position_limits[asset]
            else:
                desired_positions[asset] = current_position

        # Trading function for Fintech Token using EMA and momentum.
        def trade_fintech_token_simple():
            asset = "Fintech Token"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            ema_window = 3
            padded_history = self.get_recent_history(asset, ema_window)
            ema = ema_indicator(padded_history, ema_window)
            desired_position = current_position
            if current_price < ema:
                desired_position = position_limits[asset]
            elif current_price > ema:
                desired_position = -position_limits[asset]
            # Use actual (unpadded) data for momentum check.
            if strictly_increasing(self.data[asset], 5):
                desired_position = position_limits[asset]
            elif strictly_decreasing(self.data[asset], 5):
                desired_position = -position_limits[asset]
            desired_positions[asset] = desired_position

        # Trading function for Red Pens (uses simple thresholds; no indicator padding needed).
        def trade_red_pens_simple():
            asset = "Red Pens"
            current_price = self.get_current_price(asset)
            current_position = current_positions.get(asset, 0)
            trade_size = 10000  # Smaller than the limit so that we do not exceed the total budget
            if current_price < 2.23:
                desired_positions[asset] = trade_size
            elif current_price > 2.42:
                desired_positions[asset] = -trade_size
            else:
                desired_positions[asset] = current_position

        # Execute trading functions in sequence.
        trade_fun_drink()
        trade_uq_dollar()
        trade_goober_eats()
        trade_thrifted_jeans()
        trade_fintech_token_simple()
        trade_coffee_simple()
        trade_red_pens_simple()


        # Update daily spending as the total absolute value of desired positions.
        total_spending = 0
        for instr in self.instruments:
            total_spending += abs(desired_positions[instr] * self.get_current_price(instr))
        self.daily_spending[self.day] = total_spending

        """
        Look back on old commits for things like avg spending per asset
        """

        return desired_positions
