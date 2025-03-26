from utils.tools import ema_indicator, sma_indicator, bollinger_bands, rsi_indicator

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
        self.day = 0  # Current trading day.
        self.positions = positions  # Current positions.

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
        current_positions = self.positions
        position_limits = self.position_limits

        # Initialise desired positions for all instruments.
        desired_positions = {instr: 0 for instr in position_limits}

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

        # --- Execute Trading Functions ---
        trade_fun_drink()
        trade_uq_dollar()
        trade_fintech_token()

        # --- Close all trades on 2nd last day ---
        if self.day == 364:
            desired_positions = {instr: 0 for instr in position_limits}

        return desired_positions
