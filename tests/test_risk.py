"""Tests for risk calculation functions."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.risk import calculate_historical_var


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
