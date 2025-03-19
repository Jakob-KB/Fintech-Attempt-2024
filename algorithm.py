import numpy as np


# Custom trading Algorithm
class Algorithm():

    ########################################################
    # NO EDITS REQUIRED TO THESE FUNCTIONS
    ########################################################
    # FUNCTION TO SETUP ALGORITHM CLASS
    def __init__(self, positions, config: dict={}):
        # Initialise data stores:
        # Historical data of all instruments
        self.data = {}

        # Initialise position limits
        self.positionLimits = {}

        # Initialise the current day as 0
        self.day = 0

        # Initialise the current positions
        self.positions = positions

        # My configs
        self.lower_bound = config.get("lower_bound", 99)
        self.upper_bound = config.get("upper_bound", 101)

    # Helper function to fetch the current price of an instrument
    def get_current_price(self, instrument):
        # return most recent price
        return self.data[instrument][-1]

    ########################################################

    # RETURN DESIRED POSITIONS IN DICT FORM
    def get_positions(self):
        # Get current position
        currentPositions = self.positions

        # Get position limits
        positionLimits = self.positionLimits

        # Declare a store for desired positions
        desiredPositions = {}
        # Loop through all the instruments you can take positions on.
        for instrument, positionLimit in positionLimits.items():
            # For each instrument initialise desired position to zero
            desiredPositions[instrument] = 0

        # IMPLEMENT CODE HERE TO DECIDE WHAT POSITIONS YOU WANT
        #######################################################################

        if self.get_current_price("UQ Dollar") < self.lower_bound:  # Long
            desiredPositions["UQ Dollar"] = positionLimits["UQ Dollar"]

        elif self.get_current_price("UQ Dollar") > self.upper_bound: # Short
            desiredPositions["UQ Dollar"] = -(positionLimits["UQ Dollar"])

        else:  # if price is within these ranges close the current position
            desiredPositions["UQ Dollar"] = 0

        #######################################################################
        # Return the desired positions
        return desiredPositions