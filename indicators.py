import numpy as np
import pandas as pd


def compute_SMA(df, window=7):
    """
    Compute the Simple Moving Average (SMA) for the Price column.

    The SMA is the unweighted mean of the previous 'window' prices,
    which helps to smooth out short-term fluctuations and highlight longer-term trends.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        window (int): Number of periods over which to calculate the average.

    Returns:
        pd.Series: SMA values.
    """
    # Rolling mean over the specified window.
    return df['Price'].rolling(window=window, min_periods=window).mean()


def compute_EMA(df, span):
    """
    Compute the Exponential Moving Average (EMA) for the Price column.

    The EMA gives more weight to recent prices, making it more responsive to new information.
    It is often used to identify trend direction and potential support/resistance levels.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        span (int): Span parameter for the EMA.

    Returns:
        pd.Series: EMA values.
    """
    # Exponential weighted average with the given span.
    return df['Price'].ewm(span=span, adjust=False).mean()


def compute_BollingerBands(df, window, num_std=2):
    """
    Compute Bollinger Bands based on the SMA and rolling standard deviation.

    Bollinger Bands are volatility indicators that consist of:
      - A middle band: the SMA over a specified window.
      - An upper band: SMA plus a multiple (num_std) of the rolling standard deviation.
      - A lower band: SMA minus a multiple (num_std) of the rolling standard deviation.

    These bands adjust dynamically with volatility and can help identify overbought or oversold conditions.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        window (int): Number of periods for the SMA and rolling std.
        num_std (float): Number of standard deviations for the bands.

    Returns:
        tuple: (SMA, upper_band, lower_band) as pd.Series.
    """
    # Compute the simple moving average as the middle band.
    sma = compute_SMA(df, window)
    # Compute rolling standard deviation over the same window.
    rolling_std = df['Price'].rolling(window=window, min_periods=window).std()
    # Upper band is SMA plus (num_std * rolling_std)
    upper_band = sma + num_std * rolling_std
    # Lower band is SMA minus (num_std * rolling_std)
    lower_band = sma - num_std * rolling_std
    return sma, upper_band, lower_band


def compute_RSI(df, window=7):
    """
    Compute the Relative Strength Index (RSI) for the Price column.

    The RSI is a momentum oscillator that measures the speed and change of price movements.
    It ranges from 0 to 100 and is used to identify overbought (typically above 70) or oversold (typically below 30) conditions.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        window (int): Window length for RSI calculation.

    Returns:
        pd.Series: RSI values.
    """
    # Calculate price changes.
    delta = df['Price'].diff()
    # Identify gains and losses. Gains are positive changes; losses are the absolute value of negative changes.
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    # Compute the average gain and average loss over the specified window.
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    # Avoid division by zero; replace zero losses with NaN.
    rs = avg_gain / avg_loss.replace(0, np.nan)
    # Calculate RSI based on the RS value.
    rsi = 100 - (100 / (1 + rs))
    # Fill initial NaN values with 0.
    rsi = rsi.fillna(0)
    return rsi


def compute_MACD(df, fast_span=12, slow_span=26, signal_span=9):
    """
    Compute the Moving Average Convergence Divergence (MACD) indicator.

    The MACD is a momentum indicator that shows the relationship between two EMAs:
      - The MACD line is the difference between a fast EMA and a slow EMA.
      - The signal line is an EMA of the MACD line.
      - The histogram is the difference between the MACD line and the signal line.

    This indicator is used to identify potential buy and sell signals.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        fast_span (int): Span for the fast EMA (default is 12).
        slow_span (int): Span for the slow EMA (default is 26).
        signal_span (int): Span for the signal line EMA (default is 9).

    Returns:
        tuple: (MACD_line, signal_line, histogram) as pd.Series.
    """
    # Calculate fast and slow EMAs.
    ema_fast = compute_EMA(df, fast_span)
    ema_slow = compute_EMA(df, slow_span)
    # The MACD line is the difference between the fast and slow EMAs.
    macd_line = ema_fast - ema_slow
    # The signal line is an EMA of the MACD line.
    signal_line = macd_line.ewm(span=signal_span, adjust=False).mean()
    # The histogram represents the difference between the MACD line and the signal line.
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_volatility(df, window=7):
    """
    Compute volatility as the rolling standard deviation of daily returns.

    Volatility is a measure of the dispersion of returns for a given security.
    This function calculates volatility using the standard deviation of the percentage changes in Price.

    Parameters:
        df (pd.DataFrame): DataFrame with columns "Day" and "Price".
        window (int): Window length for the rolling standard deviation.

    Returns:
        pd.Series: Volatility values.
    """
    # Calculate daily returns as the percentage change in Price.
    df['Return'] = df['Price'].pct_change()
    # Rolling standard deviation of returns represents volatility.
    return df['Return'].rolling(window=window, min_periods=window).std()
