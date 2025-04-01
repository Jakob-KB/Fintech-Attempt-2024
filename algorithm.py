from utils.tools import ema_indicator, sma_indicator, bollinger_bands, rsi_indicator, rsi_series, macd_indicator


def strictly_increasing(price_history: list, days: int) -> bool:
    if len(price_history) < days:
        return False

    # Extract the last 'days' elements
    subset = price_history[-days:]
    # Check if each element is strictly less than the next
    return all(earlier < later for earlier, later in zip(subset, subset[1:]))


def strictly_decreasing(price_history: list, days: int) -> bool:
    if len(price_history) < days:
        return False

    # Extract the last 'days' elements
    subset = price_history[-days:]
    # Check if each element is strictly greater than the next
    return all(earlier > later for earlier, later in zip(subset, subset[1:]))


# Centralized default configuration.
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
    # New parameters for our SMA-based strategy for Fun Drink.
    "Fun Drink": {
        "ema_window": 3,       # number of days to compute the SMA
        "trade_size": 10000,     # incremental trade unit
    },
}


class Algorithm:
    def __init__(self, positions, config: dict = {}):
        # Initialise historical data and position limits.
        self.data = {}  # Historical data of all instruments.
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
        self.day = 0  # Current trading day.
        self.positions = positions  # Current positions.

        self.daily_spending = {}

        # Merge the default configuration with any provided overrides.
        self.config = DEFAULT_CONFIG.copy()
        for key, params in config.items():
            if key in self.config and isinstance(params, dict):
                self.config[key].update(params)
            else:
                self.config[key] = params

    def get_current_price(self, instrument):
        # Return the most recent price for the given instrument.
        return self.data[instrument][-1]

    def get_positions(self):

        total_daily_budget = 500_000  # Basically the absolute value of the positions we are allowed to hold on any given day

        current_positions = self.positions
        position_limits = self.position_limits

        # Initialise desired positions for all instruments.
        desired_positions = {instr: 0 for instr in position_limits}

        # One day one just let it hang and go all in (adding this gave +1k of PnL)
        if self.day < 6:
            desired_positions = {instr: position_limits[instr] for instr in position_limits}

        # --- Trading Functions ---
        def trade_uq_dollar():
            current_price = self.get_current_price("UQ Dollar")
            params = self.config["UQ Dollar"]
            if current_price < 100:
                desired_positions["UQ Dollar"] = position_limits["UQ Dollar"]
            elif current_price > 100:
                desired_positions["UQ Dollar"] = -position_limits["UQ Dollar"]
            else:
                desired_positions["UQ Dollar"] = current_positions.get("UQ Dollar", 0)

        def trade_fintech_token():
            price_history = self.data["Fintech Token"]
            params = self.config["Fintech Token"]
            sma_short = sma_indicator(price_history, params["sma_short_days"])
            sma_long = sma_indicator(price_history, params["sma_long_days"])
            difference = abs(sma_short - sma_long)

            if self.day > 2:
                if sma_short > sma_long and difference > params["difference_threshold"]:
                    desired_positions["Fintech Token"] = position_limits["Fintech Token"]
                elif sma_short < sma_long and difference > params["difference_threshold"]:
                    desired_positions["Fintech Token"] = -position_limits["Fintech Token"]
                else:
                    desired_positions["Fintech Token"] = position_limits["Fintech Token"]

        def trade_fun_drink():
            current_price = self.get_current_price("Fun Drink")
            price_history = self.data["Fun Drink"]
            current_position = current_positions.get("Fun Drink", 0)
            params = self.config["Fun Drink"]
            ema_window = 3
            trade_size = position_limits["Fun Drink"]

            # By Default stay on the trade we currently have
            desired_position = current_position

            # If there isn't enough history, hold current position.
            if len(price_history) < ema_window:
                desired_positions["Fun Drink"] = desired_position
                return

            # Calculate the EMA from the most recent ema_window days
            ema = ema_indicator(price_history, ema_window)

            # Buy when current price is below EMA, sell when above.
            if current_price < ema:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > ema:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            desired_positions["Fun Drink"] = desired_position

        def trade_goober_eats():
            current_price = self.get_current_price("Goober Eats")
            price_history = self.data["Goober Eats"]
            current_position = current_positions.get("Goober Eats", 0)
            ema_window = 7
            trade_size = self.position_limits["Goober Eats"]

            # By default, stay on the trade we currently have
            desired_position = current_position

            if len(price_history) < ema_window:
                desired_positions["Goober Eats"] = desired_position
                return

            # Calculate the EMA from the most recent ema_window days
            ema = ema_indicator(price_history, ema_window)
            threshold = 0.0025

            # Buy when current price is below EMA, sell when above.
            if current_price < ema - threshold:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > ema + threshold:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            desired_positions["Goober Eats"] = desired_position

        def trade_thifted_jeans():
            asset = "Thrifted Jeans"

            current_price = self.get_current_price(asset)
            price_history = self.data[asset]
            current_position = current_positions.get(asset, 0)
            ema_window = 5
            trade_size = self.position_limits[asset]

            # By default, stay on the trade we currently have
            desired_position = current_position

            if len(price_history) < ema_window:
                desired_positions[asset] = desired_position
                return

            # Calculate the EMA from the most recent ema_window days
            ema = ema_indicator(price_history, ema_window)
            threshold = 0

            # Buy when current price is below EMA, sell when above.
            if current_price < ema - threshold:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > ema + threshold:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            # Very very simply stop loss working via momentum days
            days_back = 4
            threshold = 0.15
            USE_STOP_LOSS = False
            if self.day > days_back + 1 and USE_STOP_LOSS:
                percent_change = abs(current_price - price_history[-days_back]) / price_history[-days_back]
                if percent_change > threshold:
                    desired_position = trade_size
                elif percent_change < -threshold:
                    desired_position = -trade_size


            desired_positions[asset] = desired_position

        def trade_red_pens_simple():
            asset = "Red Pens"

            current_price = self.get_current_price(asset)
            price_history = self.data[asset]
            current_position = current_positions.get(asset, 0)
            trade_size = self.position_limits[asset]

            # By default, stay on the trade we currently have
            desired_position = current_position

            if self.day == 0:
                return

            # Buy when current price is below EMA, sell when above.
            if current_price < 2.23:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > 2.42:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            desired_positions[asset] = desired_position

        def trade_coffee():
            asset = "Coffee"

            current_price = self.get_current_price(asset)
            price_history = self.data[asset]
            current_position = current_positions.get(asset, 0)
            trade_size = self.position_limits[asset]

            # By default, stay on the trade we currently have
            desired_position = current_position

            macd_line, macd_signal, macd_hist = macd_indicator(price_history)

            current_macd_line = macd_line[-1]
            current_macd_hist = macd_hist[-1]
            current_macd_signal = macd_signal[-1]

            difference = abs(current_macd_signal - current_macd_line)
            difference_direction = current_macd_signal - current_macd_line

            difference_threshold = 0.005

            if difference > difference_threshold:
                if difference_direction > 0:
                    desired_position = trade_size
                elif difference_direction < 0:
                    desired_position = -trade_size


            desired_positions[asset] = desired_position

        def trade_coffee_simple():
            asset = "Coffee"

            current_price = self.get_current_price(asset)
            price_history = self.data[asset]
            current_position = current_positions.get(asset, 0)
            ema_window = 3
            trade_size = self.position_limits[asset]

            # By default, stay on the trade we currently have
            desired_position = current_position

            if len(price_history) < ema_window:
                desired_positions[asset] = desired_position
                return

            # Calculate the EMA from the most recent ema_window days
            ema = ema_indicator(price_history, ema_window)

            # Buy when current price is below EMA, sell when above.
            if current_price < ema:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > ema:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            desired_positions[asset] = desired_position

        def trade_fintech_token_simple():
            asset = "Fintech Token"

            current_price = self.get_current_price(asset)
            price_history = self.data[asset]
            current_position = current_positions.get(asset, 0)
            ema_window = 3
            trade_size = self.position_limits[asset]

            # By default, stay on the trade we currently have
            desired_position = current_position

            if len(price_history) < ema_window:
                desired_positions[asset] = desired_position
                return

            # Calculate the EMA from the most recent ema_window days
            ema = ema_indicator(price_history, ema_window)
            threshold = 0

            # Buy when current price is below EMA, sell when above.
            if current_price < ema + threshold:
                # Buy signal: increase position, but do not exceed the long limit.
                desired_position = trade_size
            elif current_price > ema - threshold:
                # Sell signal: decrease position, but do not exceed the short limit.
                desired_position = -trade_size
            else:
                desired_position = current_position

            # Very very simply stop loss working via momentum days
            momentum_days = 5
            if strictly_increasing(price_history, momentum_days):
                desired_position = trade_size
            elif strictly_decreasing(price_history, momentum_days):
                desired_position = -trade_size

            desired_positions[asset] = desired_position

        # --- Execute Trading Functions ---
        run_all = False
        if run_all:
            pass
        trade_fun_drink()
        trade_uq_dollar()
        trade_goober_eats()
        trade_thifted_jeans()
        trade_fintech_token_simple()
        trade_coffee_simple()

        print(str("-" * 10), "Desired Positions", str("-" * 10))
        for instr in self.instruments:
            print(f"{instr}: {desired_positions[instr]}")

        print(str("-" * 10), "Desired Positions in Cash (ABS)", str("-" * 10))
        desired_sum_to_spend = 0
        current_day_spending = {}
        for instr in self.instruments:
            desired_instr_value = abs(desired_positions[instr] * self.get_current_price(instr))
            current_day_spending[instr] = desired_instr_value
            desired_sum_to_spend += desired_instr_value
            print(f"{instr}: ${desired_instr_value}")
        self.daily_spending[self.day] = current_day_spending
        print(f"Value of total daily positions: ${desired_sum_to_spend} / ${total_daily_budget} \n")


        if desired_sum_to_spend < total_daily_budget - 85_500:
            trade_red_pens_simple()

        if self.day == 364:
            # Calculate average daily spending for each instrument over all days.
            total_days = len(self.daily_spending)  # should be 365 days
            average_spending = {instr: 0 for instr in self.instruments}

            # Sum up spending for each instrument over all days.
            for day_spending in self.daily_spending.values():
                for instr, amount in day_spending.items():
                    average_spending[instr] += amount

            # Compute average for each instrument.
            for instr in average_spending:
                average_spending[instr] /= total_days

            print("Average Daily Spending per Instrument over 365 days:")
            for instr, avg in average_spending.items():
                print(f"{instr}: ${avg:,.2f}")

        return desired_positions



"""
Current ideas for improvement:

1. look at each assets 'efficiency' in terms of how much of the total daily spending limit does it take up
and how much return do we see relative to that.
2. Look at each strategy, the percent odds that it wins on any given trade, and then the expected pay out
of any individual trade based on how far it is from something like the ema. We can then allocate spending
limit based on what is most likely to be the most profitable trades during a given period.

"""