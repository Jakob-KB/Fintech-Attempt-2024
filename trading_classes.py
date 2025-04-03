class Trade:
    def __init__(self, asset, entry_day, entry_price, position):
        """
        Initialize a new trade.

        Parameters:
            asset (str): The asset symbol.
            entry_day (int): The day the trade was initiated.
            entry_price (float): The entry price.
            position (int): The size of the position (positive for long, negative for short).
        """
        self.asset = asset
        self.entry_day = entry_day
        self.entry_price = entry_price
        self.position = position
        self.exit_day = None
        self.exit_price = None
        self.realised_value = None
        self.cost_to_hold = abs(entry_price * position)
        self.position_prices = [entry_price]
        self.ev_history = []  # Record of expected values while the trade is open

    def update(self, current_day, current_price, exit_condition):
        """Update cost-to-hold, record the latest price, and save the current expected value."""
        self.cost_to_hold = abs(current_price * self.position)
        self.position_prices.append(current_price)
        ev = self.calculate_expected_value(exit_condition)
        self.ev_history.append(ev)

    def close(self, exit_day, exit_price):
        """
        Close the trade, compute the realised value, and print the EV history.
        """
        self.exit_day = exit_day
        self.exit_price = exit_price
        if self.position > 0:
            # For long trades: profit if exit > entry
            self.realised_value = (exit_price - self.entry_price) * self.position
        else:
            # For short trades: profit if exit < entry
            self.realised_value = (self.entry_price - exit_price) * abs(self.position)
        # Print EV history and realised value upon closing the trade.
        print(f"Trade for {self.asset} closed on day {exit_day} at price {exit_price}")
        print(f"EV History: {self.ev_history}")
        print(f"Realised Value: {self.realised_value}")

    def calculate_expected_value(self, exit_condition):
        """
        Calculate the expected value (EV) based on an exit condition price.

        Parameters:
            exit_condition (float): The price level used as a benchmark for EV.

        Returns:
            float: The expected value.
        """
        avg_long_exit = 100
        avg_short_exit = 100
        dynamic_exit = avg_long_exit if self.position > 0 else avg_short_exit
        expected_exit_value = dynamic_exit * self.position
        return expected_exit_value - (self.entry_price * self.position)

    def performance_summary(self, exit_condition):
        """
        Returns a summary of the trade's performance.

        Parameters:
            exit_condition (float): The benchmark exit price for EV calculation.

        Returns:
            dict: A summary of key trade metrics.
        """
        ev = self.calculate_expected_value(exit_condition)
        eff = None
        if len(self.position_prices) >= 2:
            # Efficiency can be defined in many ways; here we show a ratio relative to the last price.
            eff = ev / self.position_prices[-1]
        return {
            "asset": self.asset,
            "entry_day": self.entry_day,
            "entry_price": self.entry_price,
            "exit_day": self.exit_day,
            "exit_price": self.exit_price,
            "position": self.position,
            "cost_to_hold": self.cost_to_hold,
            "expected_value": ev,
            "realised_value": self.realised_value,
            "position_prices": self.position_prices,
            "position_efficiency": eff,
            "ev_history": self.ev_history
        }


class UQDollarStrategy:
    def __init__(self, algo, trade_size=650, exit_condition=100):
        """
        Initialize the UQ Dollar trading strategy.

        Parameters:
            algo: Reference to the parent algorithm object (provides access to data, day, etc.)
            trade_size (int): The size of the trade.
            exit_condition (float): The benchmark price to calculate expected value.
        """
        self.algo = algo
        self.trade_size = trade_size
        self.exit_condition = exit_condition
        self.active_trade = None

    def evaluate(self):
        """
        Evaluate the current market conditions for UQ Dollar.
        If the desired position differs from the active trade's position, close the current trade (if any)
        and open a new one.

        Returns:
            dict: A performance summary of the current trade.
        """
        asset = "UQ Dollar"
        current_price = self.algo.get_current_price(asset)
        # Determine the desired position based on current price relative to the exit condition.
        if current_price < self.exit_condition:
            desired_position = self.trade_size
        elif current_price > self.exit_condition:
            desired_position = -self.trade_size
        else:
            # If current_price equals the exit condition, hold the current trade if it exists,
            # otherwise default to no position.
            desired_position = self.active_trade.position if self.active_trade is not None else 0

        # If there's an active trade, update it to record the latest EV.
        if self.active_trade is not None:
            self.active_trade.update(self.algo.day, current_price, self.exit_condition)
            # If the active trade's position is not what we desire, then close it.
            if desired_position != self.active_trade.position:
                self.active_trade.close(self.algo.day, current_price)
                print(f"Trade for {asset} closed on day {self.algo.day} at price {current_price}")
                # Optionally store the closed trade for logging.
                self.algo.trades.setdefault(asset, []).append(self.active_trade)
                # Open a new trade with the desired position.
                self.active_trade = Trade(asset, self.algo.day, current_price, desired_position)
                # Record initial EV immediately.
                self.active_trade.update(self.algo.day, current_price, self.exit_condition)
                print(f"Opened new trade for {asset} on day {self.algo.day} at price {current_price}")
        else:
            # No active trade: open a new one and record the initial EV.
            self.active_trade = Trade(asset, self.algo.day, current_price, desired_position)
            self.active_trade.update(self.algo.day, current_price, self.exit_condition)
            print(f"Opened new trade for {asset} on day {self.algo.day} at price {current_price}")

        # Calculate expected value and print trade type info.
        ev = self.active_trade.calculate_expected_value(self.exit_condition)
        trade_type = "Long" if self.active_trade.position > 0 else "Short"
        if self.algo.day >= 2:
            print(f"Day {self.algo.day} - {trade_type} Trade EV for {asset}: {ev} at price {current_price}")

        return self.active_trade.performance_summary(self.exit_condition)
