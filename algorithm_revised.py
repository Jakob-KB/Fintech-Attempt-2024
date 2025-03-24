import logging
import numpy as np

# Custom trading Algorithm
class Algorithm():
    ########################################################
    # NO EDITS REQUIRED TO THESE FUNCTIONS
    ########################################################
    # FUNCTION TO SETUP ALGORITHM CLASS
    def __init__(self, positions):
        # Initialise data stores
        self.data = {}
        self.instruments = [
            "Fintech Token",
            "Fun Drink",
            "Red Pens",
            "Thrifted Jeans",
            "UQ Dollar",
            "Coffee",
            "Coffee Beans",
            "Goober Eats",
            "Milk"
        ]
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
        self.daily_limit = 50000

        self.day = 0

        # Initialise the current positions
        self.positions = positions

        self.trades = {}

    # Helper function to fetch the current price of an instrument
    def get_current_price(self, instrument):
        # return most recent price
        return self.data[instrument][-1]

    ########################################################

    # RETURN DESIRED POSITIONS IN DICT FORM
    def get_positions(self):
        desired_positions = {}
        current_positions = self.positions
        for instrument in self.instruments:
            desired_positions[instrument] = current_positions[instrument]


        # IMPLEMENT CODE HERE TO DECIDE WHAT POSITIONS YOU WANT
        #######################################################################

        # Example logic for UQ Dollar
        price = self.get_current_price("UQ Dollar")
        if price < 100:  # If less than 100 long with pos limit
            desired_positions["UQ Dollar"] = 650
        elif price > 100:  # If greater than 100 short with pos limit
            desired_positions["UQ Dollar"] = -650
        else:  # Otherwise just keep our current position
            desired_positions["UQ Dollar"] = current_positions["UQ Dollar"]

        #######################################################################

        # Return the desired positions
        return desired_positions
