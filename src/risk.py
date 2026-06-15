"""Risk calculation helpers for the Portfolio Risk Dashboard."""

import numpy as np
import pandas as pd


def calculate_historical_var(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """Calculate historical Value at Risk from daily portfolio returns.

    Value at Risk estimates a loss threshold from past returns. At 95%
    confidence, this historical method uses the 5th percentile daily return and
    reports the loss as a positive number.
    """
    if confidence_level <= 0 or confidence_level >= 1:
        raise ValueError("confidence_level must be between 0 and 1")

    percentile = (1 - confidence_level) * 100
    var_return = np.percentile(portfolio_returns, percentile)
    historical_var = max(0.0, -var_return)

    return float(historical_var)


def calculate_stress_test_loss(
    weights: dict,
    shocks: dict,
    portfolio_value: float = 10000,
) -> dict:
    """Calculate portfolio impact from hypothetical ticker-level shocks.

    Stress testing applies assumed market shocks to each holding to estimate how
    the total portfolio would respond. It is a scenario analysis tool, not a
    prediction of what markets will do.
    """
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be greater than 0")
    if not weights:
        raise ValueError("weights must not be empty")

    missing_shocks = [ticker for ticker in weights if ticker not in shocks]
    if missing_shocks:
        missing = ", ".join(missing_shocks)
        raise ValueError(f"Missing shock(s) for ticker(s): {missing}")

    portfolio_impact_percent = sum(
        weights[ticker] * shocks[ticker] for ticker in weights
    )
    portfolio_impact_value = portfolio_value * portfolio_impact_percent
    stressed_portfolio_value = portfolio_value + portfolio_impact_value

    return {
        "portfolio_impact_percent": portfolio_impact_percent,
        "portfolio_impact_value": portfolio_impact_value,
        "stressed_portfolio_value": stressed_portfolio_value,
    }


def run_monte_carlo_simulation(
    portfolio_returns: pd.Series,
    num_simulations: int = 1000,
    num_days: int = 252,
    initial_value: float = 10000,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generate illustrative portfolio value paths using historical returns.

    A Monte Carlo simulation creates many scenario paths by drawing
    random daily returns. This simple version uses the portfolio's historical
    average return and volatility, so it is a risk illustration rather than a
    market forecast.
    """
    if portfolio_returns.empty:
        raise ValueError("portfolio_returns must not be empty")
    if num_simulations <= 0:
        raise ValueError("num_simulations must be greater than 0")
    if num_days <= 0:
        raise ValueError("num_days must be greater than 0")
    if initial_value <= 0:
        raise ValueError("initial_value must be greater than 0")

    mean_return = portfolio_returns.mean()
    return_volatility = portfolio_returns.std()

    random_generator = np.random.default_rng(random_seed)
    simulated_returns = random_generator.normal(
        loc=mean_return,
        scale=return_volatility,
        size=(num_days, num_simulations),
    )

    starting_values = np.full((1, num_simulations), initial_value)
    simulated_values = initial_value * (1 + simulated_returns).cumprod(axis=0)
    simulation_paths = np.vstack([starting_values, simulated_values])

    columns = [f"Simulation {number}" for number in range(1, num_simulations + 1)]

    return pd.DataFrame(simulation_paths, columns=columns)
