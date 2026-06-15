"""Return and performance metric calculations for the Portfolio Risk Dashboard."""

import pandas as pd


def calculate_daily_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate each ticker's daily percentage return from closing prices.

    A daily return measures how much a price changed from one trading day to the
    next. For example, a move from 100 to 110 is a 10% daily return.
    """
    price_table = price_df.pivot(index="Date", columns="Ticker", values="Close")
    daily_returns = price_table.pct_change().dropna()

    return daily_returns


def calculate_cumulative_returns(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total compounded return over time from daily returns.

    Cumulative return shows how much an investment has gained or lost since the
    start of the period, assuming each day's return builds on previous days.
    """
    cumulative_returns = (1 + returns_df).cumprod() - 1

    return cumulative_returns
