"""Tests for risk calculation functions."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pandas.testing import assert_frame_equal

from src.risk import calculate_historical_var, run_monte_carlo_simulation


def test_calculate_historical_var_uses_lower_tail_percentile():
    """Calculate 95% historical VaR from simple known portfolio returns."""
    portfolio_returns = pd.Series([-0.10, -0.05, 0.00, 0.05, 0.10])

    result = calculate_historical_var(portfolio_returns, confidence_level=0.95)

    assert result == pytest.approx(0.09)


def test_calculate_historical_var_accepts_different_confidence_level():
    """Calculate historical VaR using the percentile implied by confidence."""
    portfolio_returns = pd.Series([-0.10, -0.05, 0.00, 0.05, 0.10])

    result = calculate_historical_var(portfolio_returns, confidence_level=0.80)

    assert result == pytest.approx(0.06)


def test_calculate_historical_var_raises_value_error_for_invalid_confidence():
    """Raise a clear error when confidence level is outside the valid range."""
    portfolio_returns = pd.Series([-0.10, -0.05, 0.00, 0.05, 0.10])

    with pytest.raises(ValueError, match="confidence_level must be between 0 and 1"):
        calculate_historical_var(portfolio_returns, confidence_level=1.00)


def test_run_monte_carlo_simulation_returns_expected_shape():
    """Return one column per simulation and one extra row for the start value."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    result = run_monte_carlo_simulation(
        portfolio_returns,
        num_simulations=3,
        num_days=5,
        initial_value=1000,
    )

    assert result.shape == (6, 3)


def test_run_monte_carlo_simulation_first_row_equals_initial_value():
    """Start every simulation path at the same initial portfolio value."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    result = run_monte_carlo_simulation(
        portfolio_returns,
        num_simulations=3,
        num_days=5,
        initial_value=1000,
    )

    assert result.iloc[0].tolist() == [1000, 1000, 1000]


def test_run_monte_carlo_simulation_same_seed_gives_same_result():
    """Use the random seed to make simulations reproducible in tests."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    first_result = run_monte_carlo_simulation(
        portfolio_returns,
        num_simulations=3,
        num_days=5,
        random_seed=7,
    )
    second_result = run_monte_carlo_simulation(
        portfolio_returns,
        num_simulations=3,
        num_days=5,
        random_seed=7,
    )

    assert_frame_equal(first_result, second_result)


def test_run_monte_carlo_simulation_raises_value_error_for_empty_returns():
    """Raise a clear error when there are no historical returns."""
    with pytest.raises(ValueError, match="portfolio_returns must not be empty"):
        run_monte_carlo_simulation(pd.Series(dtype=float))


def test_run_monte_carlo_simulation_raises_value_error_for_bad_simulation_count():
    """Raise a clear error when the requested simulation count is invalid."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    with pytest.raises(ValueError, match="num_simulations must be greater than 0"):
        run_monte_carlo_simulation(portfolio_returns, num_simulations=0)


def test_run_monte_carlo_simulation_raises_value_error_for_bad_day_count():
    """Raise a clear error when the requested number of future days is invalid."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    with pytest.raises(ValueError, match="num_days must be greater than 0"):
        run_monte_carlo_simulation(portfolio_returns, num_days=0)


def test_run_monte_carlo_simulation_raises_value_error_for_bad_initial_value():
    """Raise a clear error when the starting portfolio value is invalid."""
    portfolio_returns = pd.Series([0.01, -0.02, 0.03, 0.00])

    with pytest.raises(ValueError, match="initial_value must be greater than 0"):
        run_monte_carlo_simulation(portfolio_returns, initial_value=0)
