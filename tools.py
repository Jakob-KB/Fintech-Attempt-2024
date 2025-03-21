def average_price_over_last_X_days(stock_price_history, days):
    return sum(stock_price_history[-days:]) / days