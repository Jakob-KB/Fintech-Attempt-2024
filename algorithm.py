
from tools import average_price_over_last_X_days

class Algorithm():
    def __init__(self, positions, config: dict={}):
        # Initialise data stores:
        self.data = {}              # Historical data of all instruments
        self.positionLimits = {}    # Initialise position limits
        self.day = 0                # Initialise the current day as 0
        self.positions = positions  # Initialise the current positions

        # My configs

        ########################### MY CONFIGS ################################

        ##### UQ Dollar #####
        self.lower_bound = config.get("lower_bound", 100)
        self.upper_bound = config.get("upper_bound", 100)

        #######################################################################

    def get_current_price(self, instrument):
        # return most recent price
        return self.data[instrument][-1]

    def get_positions(self):
        currentPositions = self.positions  # Current positions we are holding
        position_limits = self.positionLimits  # Maximum long or short position we can hold


        # Declare a store for desired positions
        desired_positions = {}
        # Instability start the day wanting to set all positions to 0 (I.e. close all positions)
        for instrument, positionLimit in position_limits.items():
            desired_positions[instrument] = 0

        def price_history(stock):
            return self.data[stock]

        def current_price(stock):
            return self.data[stock][-1]

        def open_long_position(stock, amount):
            desired_positions[stock] += amount

        def open_short_position(stock, amount):
            desired_positions[stock] += amount

        def average_price(stock, days):
            return average_price_over_last_X_days(stock, days)

        def close_existing_position(stock):
            desired_positions[stock] = 0

        def current_position(stock):
            return currentPositions[stock]

        # IMPLEMENT CODE HERE TO DECIDE WHAT POSITIONS YOU WANT
        #######################################################################

        def trade_uq_dollar():
            # Check price is ABOVE what it 'should' be
            if current_price("UQ Dollar") < self.lower_bound:
                # Close and take profit (or loss) on any current position we have
                close_existing_position("UQ Dollar")

                # Open a long position on the UQ Dollar (expecting it will go up)
                open_long_position("UQ Dollar", amount=650)

            # Check price is BELOW what it 'should' be
            elif current_price("UQ Dollar") > self.upper_bound:
                # Close and take profit (or loss) on any current position we have
                close_existing_position("UQ Dollar")
                # Open a short position on the UQ Dollar (expecting it will go up)
                open_short_position("UQ Dollar", amount=-650)


            # Otherwise we just keep our any existing position open
            else:
                desired_positions["UQ Dollar"] = current_position("UQ Dollar")

        def trade_fintech_token():
            # Calculate a short and long term moving average
            short_term_moving_average = average_price("Fintech Token", days=7)
            long_term_moving_average = average_price("Fintech Token", days=28)

            # Current ABS difference in the short and long term moving average
            difference = abs(short_term_moving_average - long_term_moving_average)

            # The difference in short and long term averages that we think is significant enough to act on
            threshold = 50

            if short_term_moving_average > long_term_moving_average and difference > threshold:
                open_long_position("Fintech Token", amount=100)






        trade_uq_dollar()




        #######################################################################
        # Return the desired positions
        return desired_positions