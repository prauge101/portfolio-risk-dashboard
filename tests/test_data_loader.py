"""Tests for CSV price data loading."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_loader import load_price_data


def test_load_price_data_loads_sample_csv():
    """Load the sample CSV and return sorted price data with datetime dates."""
    data = load_price_data("data/sample_prices.csv")

    assert list(data.columns) == ["Date", "Ticker", "Close"]
    assert len(data) == 18
    assert pd.api.types.is_datetime64_any_dtype(data["Date"])
    assert data.iloc[0]["Ticker"] == "ALPHA"
    assert data.iloc[-1]["Ticker"] == "GAMMA"
    assert data.equals(data.sort_values(["Date", "Ticker"]).reset_index(drop=True))


def test_load_price_data_raises_value_error_for_missing_columns(tmp_path):
    """Raise a clear error when the CSV does not contain all required columns."""
    bad_csv = tmp_path / "missing_close.csv"
    bad_csv.write_text("Date,Ticker\n2026-01-02,ALPHA\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required column\\(s\\): Close"):
        load_price_data(str(bad_csv))
