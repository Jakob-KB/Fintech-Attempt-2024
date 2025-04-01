"""
Only made these myself as we cant use external libraries like stock-indicators or yfinance
"""
import pandas as pd


def sma_indicator(stock_price_history, days) -> float:
    sum_of_prices = 0
    if days == 0:
        return 0
    for price in stock_price_history[-days:]:
        sum_of_prices += int(price)
    average_price = sum_of_prices / days

    return average_price


def ema_indicator(price_history: list[float], window: int) -> float:
    price_history = price_history[-window:]
    alpha = 2 / (window + 1)
    ema = price_history[0]
    for price in price_history[1:]:
        ema = (price - ema) * alpha + ema

    return ema

def rsi_indicator(stock_price_history, days) -> float:
    # Not enough data to compute changes
    if len(stock_price_history) < days + 1:
        return 50.0  # neutral RSI if data is insufficient

    total_gain = 0
    total_loss = 0
    # Calculate gains and losses over the last 'days' changes
    # (iterate over the last 'days' differences)
    for i in range(-days, 0):
        current_price = int(stock_price_history[i])
        previous_price = int(stock_price_history[i - 1])
        change = current_price - previous_price
        if change > 0:
            total_gain += change
        else:
            total_loss += abs(change)

    average_gain = total_gain / days
    average_loss = total_loss / days

    # Avoid division by zero
    if average_loss == 0:
        return 100.0

    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_series(prices: list[float], window: int) -> list[float]:
    rsi_list = [None] * window
    gains = []
    losses = []
    for i in range(1, window + 1):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    rsi_list.append(rsi)
    for i in range(window + 1, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(change, 0)
        loss = max(-change, 0)
        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_list.append(rsi)
    return rsi_list



def bollinger_bands(stock_price_history, days, num_std=2) -> tuple[float, float, float]:
    # Calculate the simple moving average for the last 'days'
    middle_band = sma_indicator(stock_price_history, days)

    # Compute the standard deviation for the last 'days'
    sum_sq_diff = 0
    for price in stock_price_history[-days:]:
        diff = int(price) - middle_band
        sum_sq_diff += diff ** 2
    std_dev = (sum_sq_diff / days) ** 0.5

    upper_band = middle_band + num_std * std_dev
    lower_band = middle_band - num_std * std_dev

    return middle_band, upper_band, lower_band


def macd_indicator(prices: list[float],
                   short_window: int = 12,
                   long_window: int = 26,
                   signal_window: int = 9) -> tuple[list[float], list[float], list[float]]:
    """
    Compute the MACD line, Signal line, and Histogram using exponential moving averages.
    """
    # Using pandas for simplicity
    price_series = pd.Series(prices)
    ema_short = price_series.ewm(span=short_window, adjust=False).mean()
    ema_long = price_series.ewm(span=long_window, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line.tolist(), signal_line.tolist(), histogram.tolist()