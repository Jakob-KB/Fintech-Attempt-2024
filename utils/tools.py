def sma_indicator(price_series: list[float], window: int) -> list[float]:
    sma = []
    for i in range(len(price_series)):
        if i < window - 1:
            sma.append(None)
        else:
            window_prices = price_series[i - window + 1:i + 1]
            avg = sum(window_prices) / window
            sma.append(avg)
    return sma

def average_price_over_last_X_days(stock_price_history, days) -> float:
    sum_of_prices = 0
    for price in stock_price_history[-days:]:
        sum_of_prices += int(price)
    average_price = sum_of_prices / days

    return average_price

def series_data_list_to_dict(series_data_list):
    series_data_dict = {}
    day = 0
    for series_data in series_data_list:
        series_data_dict[day] = series_data
        day += 1
