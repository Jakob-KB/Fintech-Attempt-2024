# Library Imports
import os
import pandas as pd
from matplotlib.pyplot import title

from algorithm import Algorithm
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal, ROUND_HALF_UP
from matplotlib.gridspec import GridSpec
import math

import mplcursors

##############################
# Define constants
##############################
# PRODUCTS AND THEIR INDIVIDUAL BUDGETS IN $AUD
positionLimits = {
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
# TOTAL DAILY BUDGET IN $AUD
totalDailyBudget = 500000


##############################

# Trading Engine Class, Controlling Trades Tracking
class TradingEngine:
    def __init__(self, dataFolder='./data/'):
        dataFolder = "./data/unseen_data/"
        # dataFolder = "./data/historic_data/"

        # Init variables
        self.dataFolder = dataFolder
        # Store active positions
        self.positions = {}
        # Position Limits
        self.positionLimits = positionLimits
        # Daily return history of each instrument
        self.returnsHistory = {}
        # Instrument cumulative returns history
        self.cumulativeReturnsHistory = {}
        # Store position as % of limit for graphing
        self.pcPositionHistorys = {}
        # Daily return history of combined instruments
        self.totalReturnHistory = []
        # Cumulative historical value of combined instruments
        self.totalValueHistory = []
        # Total days in simulation
        self.totalDays = 0
        # Track total PNL across all instruments
        self.totalPNL = 0
        # Track pc of total budget used daily
        self.pcTotalBudget = []
        # Setup functions
        self.load_data()
        self.initialize_positions()

    # For loading in relevant data from .CSV Files
    def load_data(self):
        self.data = {}
        for file in os.listdir(self.dataFolder):
            if file.endswith('_price_history.csv'):
                instrumentName = file.split('_')[0]
                if instrumentName in positionLimits.keys():
                    filePath = os.path.join(self.dataFolder, file)
                    self.data[instrumentName] = pd.read_csv(filePath)
                else:
                    print(f"No position limit set for {instrumentName}. This dataset will not be loaded.")
        # Ensure that all data have same length of days
        numDays = len(self.data[list(self.data.keys())[0]])
        for data in self.data.values():
            # if a dataset has a different number of days, exit
            if len(data) != numDays:
                print("\nError, not all datasets are the same length.\bExiting...")
                exit(1)
        # Otherwise, all data should have the same number of days.
        self.totalDays = numDays
        # print("Datasets loaded successfully.")

    # Set initial positions to 0 for each
    def initialize_positions(self):
        for instrument in positionLimits:
            self.positions[instrument] = 0
            self.returnsHistory[instrument] = []
            self.cumulativeReturnsHistory[instrument] = []
            self.pcPositionHistorys[instrument] = []

    # Helper function to check that a given order is within the daily budget.
    # Also records the total utilisation of the daily budget.
    def notWithinBudget(self, desiredPositions, priceHistory):
        # calc total value of positions
        totVal = 0
        for instrument, history in priceHistory.items():
            pos = desiredPositions[instrument]
            price = history[-1]
            value = abs(pos * price)
            totVal += value
        # if the budget is exceeded
        if totVal > totalDailyBudget:
            print("#########")
            print(f"Over budget by ${totVal - totalDailyBudget}.")
            # display values of each instrument position.
            for instrument, prcHistory in priceHistory.items():
                pos = desiredPositions[instrument]
                price = prcHistory[-1]
                value = abs(pos * price)
                totVal += value
                print(f"{instrument} position value: ${value}.")
            print("#########")
            # record zero as daily position used of budget, as position will be reset to zero
            self.pcTotalBudget.append(0)
            # return true, as desired position not within budget.
            return True
        # within daily budget, so record % usage
        pcBudgetUsage = round(totVal * 100 / totalDailyBudget, 2)
        self.pcTotalBudget.append(pcBudgetUsage)
        # return false, as within the daily budget
        return False

    # Process submitted algorithm
    def run_algorithms(self, algorithmsInstance, output_daily_to_CLI = True):
        # Loop through each day of data (leaving the last)
        for day in range(self.totalDays):
            # Get current data history at this point in time
            historicalData = {}
            for instrument, priceData in self.data.items():
                # Fetch all relevant data
                priceHistory = priceData['Price'][:day + 1].tolist()
                # Add them to the historicalData store
                historicalData[instrument] = priceHistory
                # Update the algorithms instance with the new information
            algorithmsInstance.day = day
            algorithmsInstance.data = historicalData
            algorithmsInstance.positions = self.positions
            algorithmsInstance.positionLimits = self.positionLimits
            # Now get the desired positions from the competitors algorithm
            desiredPositions = algorithmsInstance.get_positions()

            # Check if the desired positions are within total budget
            if self.notWithinBudget(desiredPositions, historicalData):
                # Set all desired positions to zero
                for instrument in desiredPositions.keys():
                    desiredPositions[instrument] = 0
                print(f"REQUESTED POSIITONS EXCEED DAILY BUDGET OF: ${totalDailyBudget}.")
                print(f"SET ALL DESIRED POSITIONS FOR DAY {day} TO ZERO.")

            # Store total return for the day
            dailyReturn = 0
            # Process profit/loss for each instrument:
            for instrument, priceData in self.data.items():
                # Perform desired position quality checks (int and within limits)
                if (type(desiredPositions[instrument]) != type(1) or  # not an int
                        abs(desiredPositions[instrument]) > self.positionLimits[instrument]  # not within limits
                ):
                    # Incorrect value provided. Skip
                    print(f"Position given for {instrument} on day {day} invalid.")
                    print(f"Position given was {desiredPositions[instrument]}.")
                    print(f"The limit for this instrument today is: {self.positionLimits[instrument]}")
                    print(f"Setting desired position to zero units.")
                    # Set zero
                    desiredPositions[instrument] = 0
                # Calculate PNL if not day 0
                if day != 0:
                    existingPosition = self.positions[instrument]
                    currPrice = priceData["Price"][day]
                    lastPrice = priceData["Price"][day - 1]
                    instrumentPNL = existingPosition * (currPrice - lastPrice)
                    instrumentPNL = quantize_decimal(instrumentPNL, 2)
                    self.returnsHistory[instrument].append(instrumentPNL)
                    self.cumulativeReturnsHistory[instrument].append(
                        instrumentPNL + self.cumulativeReturnsHistory[instrument][-1]
                    )
                    # add it to the daily return
                    dailyReturn += instrumentPNL
                else:
                    # No trades executed first day
                    self.returnsHistory[instrument].append(0)
                    self.cumulativeReturnsHistory[instrument].append(0)
            # Store positions in historical tracker for graphing
            for instrument, desiredPosition in desiredPositions.items():
                self.pcPositionHistorys[instrument].append(
                    round(desiredPosition * 100 / self.positionLimits[instrument]))
            # Add the daily return to the tracker
            self.totalReturnHistory.append(dailyReturn)
            # Update total PNL
            self.totalPNL += dailyReturn
            # Display PNL
            if output_daily_to_CLI:
                print(f"Total PNL @ Day {day}: {self.totalPNL}")
            # Update total Value
            self.totalValueHistory.append(self.totalPNL)
            # Update simluator information
            self.positions = desiredPositions

    def plot_instrument_details(self, instrument):
        # Verify that the instrument's data is loaded.
        if instrument not in self.data:
            print(f"Instrument {instrument} data not found.")
            return

        # Retrieve price data and position history.
        prices = self.data[instrument]['Price']
        positions_pc = self.pcPositionHistorys[instrument]  # Position size in % of limit.

        # Initialize lists to hold day indices for trade events.
        long_days = []
        short_days = []
        close_days = []

        # Determine trade events by comparing consecutive days:
        # - Long entry: from 0 to positive.
        # - Short entry: from 0 to negative.
        # - Close: from non-zero to 0.
        # Also treat sign changes as a close and new entry.
        prev = 0
        for day, pos in enumerate(positions_pc):
            if day == 0:
                prev = pos
                continue
            if prev == 0 and pos > 0:
                long_days.append(day)
            elif prev == 0 and pos < 0:
                short_days.append(day)
            elif prev != 0 and pos == 0:
                close_days.append(day)
            elif prev > 0 and pos < 0:
                close_days.append(day)
                short_days.append(day)
            elif prev < 0 and pos > 0:
                close_days.append(day)
                long_days.append(day)
            prev = pos

        # Create a single figure and axis.
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot the price data.
        ax.plot(prices, label=f'{instrument} Price', color='black')

        # Add scatter plots for trade markers.
        if long_days:
            ax.scatter(long_days, prices.iloc[long_days], marker='^', color='green',
                       s=100, label='Long Entry')
        if short_days:
            ax.scatter(short_days, prices.iloc[short_days], marker='v', color='red',
                       s=100, label='Short Entry')
        if close_days:
            ax.scatter(close_days, prices.iloc[close_days], marker='o', facecolors='none',
                       edgecolors='blue', s=100, label='Close Position')

        ax.set_title(f"{instrument} Price and Trade Markers Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price ($)")
        ax.legend()
        plt.tight_layout()

        # Add the built-in cursor widget (crosshair) from matplotlib.widgets.
        from matplotlib.widgets import Cursor
        cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

        # Create an annotation that will display the current x and y.
        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        # Update the annotation on left mouse press.
        def on_mouse_press(event):
            if event.inaxes == ax and event.button == 1:
                annot.xy = (event.xdata, event.ydata)
                annot.set_text(f"Day: {event.xdata:.0f}\nValue: {event.ydata:.2f}")
                annot.set_visible(True)
                fig.canvas.draw_idle()

        # Hide the annotation on mouse release.
        def on_mouse_release(event):
            annot.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("button_press_event", on_mouse_press)
        fig.canvas.mpl_connect("button_release_event", on_mouse_release)

        plt.show()

    def plot_returns(self):
        # Set figure size
        fig = plt.figure(figsize=(16, 9))
        gs = GridSpec(16, 16, figure=fig)
        # Adjust spacing between subplots
        fig.subplots_adjust(wspace=10, hspace=10)
        ax1 = fig.add_subplot(gs[:8, 8:])
        ax2 = fig.add_subplot(gs[8:12, 8:])
        ax3 = fig.add_subplot(gs[:8, :8])
        ax4 = fig.add_subplot(gs[12:, 8:])
        ax5 = fig.add_subplot(gs[8:, :8])
        # Print metrics
        print('#' * 50)
        print(f"Total PNL ($): {self.totalPNL}")
        print('#' * 50)
        for instrument, returns in self.cumulativeReturnsHistory.items():
            instrumentReturn = returns[-1]
            print(f"{instrument} Returns ($): {instrumentReturn}")
        print('#' * 50)
        # Store the lines for toggling visibility
        lines = []
        # Plot individual instrument returns
        for instrument, returns in self.cumulativeReturnsHistory.items():
            line, = ax1.plot(returns, label=instrument)
            lines.append(line)
            # Plot the point at the final value
            ax1.scatter(len(returns) - 1, returns[-1], color='red', zorder=5)
            ax1.annotate(f'{returns[-1]:.2f}', (len(returns) - 1, returns[-1]), textcoords="offset points", xytext=(0, 10), ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        legend1 = ax1.legend()
        ax1.set_title('Individual Instrument Cumulative P&L ($AUD)')
        # Plot historical instrument positions
        for instrument, returns in self.pcPositionHistorys.items():
            line, = ax4.plot(returns, label=instrument, linewidth=1, alpha=1)
            lines.append(line)
        ax4.set_title(r'Historical Instrument Position (% of limit)')
        # Plot total return history
        line, = ax3.plot(self.totalValueHistory, label='Total Return', color='black')
        lines.append(line)
        # Plot a point at the final value of total return
        ax3.scatter(len(self.totalValueHistory) - 1, self.totalValueHistory[-1], color='red', zorder=5)
        ax3.annotate(f'{self.totalValueHistory[-1]:.2f}', (len(self.totalValueHistory) - 1, self.totalValueHistory[-1]),
                     textcoords="offset points", xytext=(0, 10), ha='center',
                     bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        legend3 = ax3.legend()
        ax3.set_title('Cumulative Profit & Loss ($AUD)')
        # Plot individual instrument historical P&L
        for instrument, returns in self.returnsHistory.items():
            line, = ax2.plot(returns, label=instrument)
            lines.append(line)
        ax2.set_title(r'Daily Individual P&L ($AUD)')
        # Plot daily budget usage graph
        line, = ax5.plot(self.pcTotalBudget, label='Budget Utilisation', color='black')
        ax5.set_title('Percentage of Total Daily Limit Utilised (%)')
        ax5.set_ylim(0, 100)

        # Handle picking legend options
        def on_pick(event):
            legend_item = event.artist
            is_visible = not legend_item.get_visible()
            legend_item.set_visible(is_visible)

            for orig_line in lines:
                if legend_item.get_label() == orig_line.get_label():
                    orig_line.set_visible(is_visible)

            fig.canvas.draw()

        # Enable picking on legend items
        for legend in [legend1, legend3]:
            for legend_item in legend.get_lines():
                legend_item.set_picker(True)
        # Connect the pick event
        fig.canvas.mpl_connect('pick_event', on_pick)
        # Save the figure
        output_dir = './simulation_results'
        os.makedirs(output_dir, exist_ok=True)
        fig.savefig(os.path.join(output_dir, 'returns_plot.png'), dpi=300)
        plt.show()
        plt.close(fig)

    def get_total_PnL(self) -> float:
        return self.totalPNL


# Function to round a float
def quantize_decimal(value, decimal_places=2):
    decimal_value = Decimal(value)
    if decimal_value % 1 == 0:  # Check if the number is an integer
        return decimal_value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    else:  # For non-integers, round to the specified decimal places
        rounding_format = '1.' + '0' * decimal_places
        return decimal_value.quantize(Decimal(rounding_format), rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    engine = TradingEngine()

    # This is dumb for the lower and upper bound, shouldn't work so well lmao but ig it does
    lower_bound = 99.999
    upper_bound = 100.001
    config = {
        "lower_bound": 99.999,
        "upper_bound": 100.001,
    }

    algorithmInstance = Algorithm(
        positions=engine.positions,
        config=config
    )
    engine.run_algorithms(algorithmInstance, output_daily_to_CLI=False)
    total_pnl = engine.get_total_PnL()
    print("Manual lower bound:", config.get("lower_bound"))
    print("Manual upper bound:", config.get("upper_bound"))
    print("Total PnL:", total_pnl)

    engine.plot_returns()
    engine.plot_instrument_details("UQ Dollar")
