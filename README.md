# Portfolio Risk Dashboard

A Python and Streamlit dashboard for analysing portfolio risk using historical market data, return calculations, volatility, drawdowns, correlation, historical Value at Risk, stress testing and Monte Carlo simulation.

## Why I Built This

I built this project as a Mechanical Engineering student applying engineering-style modelling, stress testing and quantitative analysis to financial markets and risk analytics.

The aim is to show how technical problem-solving skills can transfer into finance, fintech, risk analytics and technology consulting: cleaning data, validating assumptions, calculating risk metrics, testing calculation logic and presenting results in a clear dashboard.

## Key Features

- Demo synthetic data for quick testing
- CSV upload for custom portfolio price data
- Optional yfinance market data source
- Daily and cumulative return calculations
- Annualised volatility
- Drawdown and max drawdown
- Correlation matrix
- Portfolio weighting
- Historical 95% one-day Value at Risk
- Scenario stress testing
- Monte Carlo simulation
- Tested calculation modules using pytest

## Skills Demonstrated

- Python
- pandas
- NumPy
- Streamlit
- matplotlib
- pytest
- Financial risk analytics
- Data validation
- Scenario analysis
- Dashboard design

## Risk Metrics Explained

**Returns** show how much an asset or portfolio has gained or lost over a period. Daily returns measure one-day price changes, while cumulative returns show the compounded result over time.

**Volatility** measures how much returns move up and down. Higher volatility means the investment has had larger historical swings, which is one way to describe risk.

**Drawdown** shows how far an asset or portfolio has fallen from its previous high. Max drawdown shows the worst peak-to-trough fall in the selected period.

**Correlation** measures how closely assets move together. Low or negative correlation can indicate diversification benefits because assets may not all rise or fall at the same time.

**Value at Risk (VaR)** estimates a loss threshold based on historical returns. A 95% one-day historical VaR uses the lower 5% of daily portfolio returns to estimate a potential one-day loss level.

**Stress testing** applies hypothetical shocks, such as a 10% market fall, to estimate how the portfolio value could change under a chosen scenario.

**Monte Carlo simulation** generates many possible portfolio paths using historical average return and volatility. In this project it is a simplified uncertainty model, not a forecast of future prices.

## How To Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Required CSV Format

Upload a CSV with these columns:

```text
Date,Ticker,Close
```

Example:

```text
Date,Ticker,Close
2026-01-02,AAPL,185.64
2026-01-02,MSFT,412.21
```

## Testing

Run the test suite with:

```powershell
.\.venv\Scripts\pytest.exe tests
```

The tests cover the calculation modules for data loading, returns, volatility, drawdown, portfolio weights, Value at Risk, stress testing, Monte Carlo simulation and chart helpers.

## Limitations

- Demo data is synthetic and is not real investment data.
- yfinance data is for educational and research use only.
- Risk metrics are simplified and intended for learning.
- Historical performance does not predict future performance.
- This dashboard does not provide investment advice.

Market data is fetched using yfinance for educational and research purposes. yfinance is not affiliated with, endorsed by, or vetted by Yahoo. Data may be delayed, unavailable, or subject to Yahoo's terms of use.

## Future Improvements

- More advanced risk models
- Factor exposure analysis
- Better portfolio optimisation
- Exportable reports
- Deployment on Streamlit Community Cloud
