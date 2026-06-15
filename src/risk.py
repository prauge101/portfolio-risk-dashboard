"""Risk calculation helpers for the Portfolio Risk Dashboard."""

import numpy as np
import pandas as pd


def calculate_historical_var(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """Calculate historical Value at Risk for portfolio returns.

    Value at Risk estimates a possible loss threshold using past returns. At
    95% confidence, historical VaR looks at the worst 5% of returns and reports
    that loss as a positive number.
    """
    if confidence_level <= 0 or confidence_level >= 1:
        raise ValueError("confidence_level must be between 0 and 1")

    percentile = (1 - confidence_level) * 100
    var_return = np.percentile(portfolio_returns, percentile)
    historical_var = -var_return

    return float(historical_var)
