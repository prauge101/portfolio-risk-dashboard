"""Tests for return and performance metric calculations."""

import sys
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import calculate_cumulative_returns, calculate_daily_returns


def test_calculate_daily_returns_from_simple_prices():
    """Calculate easy-to-check daily percentage returns for each ticker."""
    price_data = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-02",
                    "2026-01-03",
                    "2026-01-03",
                ]
            ),
            "Ticker": ["ALPHA", "BETA", "ALPHA", "BETA", "ALPHA", "BETA"],
            "Close": [100.0, 200.0, 110.0, 180.0, 121.0, 198.0],
        }
    )

    result = calculate_daily_returns(price_data)

    expected = pd.DataFrame(
        {
            "ALPHA": [0.10, 0.10],
            "BETA": [-0.10, 0.10],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )
    expected.index.name = "Date"
    expected.columns.name = "Ticker"

    assert_frame_equal(result, expected)


def test_calculate_cumulative_returns_from_simple_returns():
    """Compound daily returns into cumulative returns over time."""
    returns_data = pd.DataFrame(
        {
            "ALPHA": [0.10, 0.10],
            "BETA": [-0.10, 0.10],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )
    returns_data.index.name = "Date"

    result = calculate_cumulative_returns(returns_data)

    expected = pd.DataFrame(
        {
            "ALPHA": [0.10, 0.21],
            "BETA": [-0.10, -0.01],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )
    expected.index.name = "Date"

    assert_frame_equal(result, expected)
