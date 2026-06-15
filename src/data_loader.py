"""Data loading helpers for the Portfolio Risk Dashboard."""

import pandas as pd


REQUIRED_COLUMNS = {"Date", "Ticker", "Close"}


def load_price_data(file_path: str) -> pd.DataFrame:
    """Load stock price data from a CSV file and return a clean DataFrame."""
    data = pd.read_csv(file_path)

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required column(s): {missing}")

    clean_data = data.loc[:, ["Date", "Ticker", "Close"]].copy()
    clean_data["Date"] = pd.to_datetime(clean_data["Date"])

    # Close is the end-of-day price used later to calculate returns and risk.
    clean_data = clean_data.sort_values(["Date", "Ticker"]).reset_index(drop=True)

    return clean_data
