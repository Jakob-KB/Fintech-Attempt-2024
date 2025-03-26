"""
Only made these myself as we cant use external libraries like stock-indicators or yfinance
"""



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


def macd_indicator(stock_price_history, fast_days, slow_days, signal_days) -> tuple[float, float]:
    # Ensure there's enough data to compute the slow EMA.
    if len(stock_price_history) < slow_days:
        return 0.0, 0.0

    # Calculate smoothing factors.
    fast_alpha = 2 / (fast_days + 1)
    slow_alpha = 2 / (slow_days + 1)

    # Initialize fast and slow EMAs using the simple moving average (SMA)
    # Use the first 'fast_days' and 'slow_days' values respectively.
    fast_ema = sma_indicator(stock_price_history[:fast_days], fast_days)
    slow_ema = sma_indicator(stock_price_history[:slow_days], slow_days)

    # We start the MACD series from the point where we have enough data for both EMAs.
    macd_series = []

    # Use the later of the two periods as the starting index.
    start_index = max(fast_days, slow_days)
    for price in stock_price_history[start_index:]:
        # Update EMAs using the current price.
        # Note: Using int(price) to follow your style, though typically you'd use the actual float value.
        fast_ema = (int(price) - fast_ema) * fast_alpha + fast_ema
        slow_ema = (int(price) - slow_ema) * slow_alpha + slow_ema
        macd_series.append(fast_ema - slow_ema)

    # Compute the signal line as the EMA of the MACD series.
    # Re-use the ema_indicator function. Since ema_indicator expects a list of prices,
    # we pass the macd_series and treat each MACD value similar to a price.
    signal_line = ema_indicator(macd_series, signal_days)

    # The latest MACD value is the last value in the macd_series.
    latest_macd = macd_series[-1] if macd_series else 0.0

    return latest_macd, signal_line
