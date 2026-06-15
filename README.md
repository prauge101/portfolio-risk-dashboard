# Portfolio Risk Dashboard

A beginner-friendly Python and Streamlit dashboard for analysing portfolio risk using stock price data.

This project is designed for a Mechanical Engineering student transitioning into finance, fintech, risk analytics, and consulting. The goal is to demonstrate Python, data analysis, finance concepts, testing, and clear dashboard presentation.

## Current Status

This repository contains a working MVP Streamlit dashboard using CSV price data and simple risk analytics.

The app currently supports:

- Loading price data from CSV
- Using synthetic demo data when no CSV is uploaded
- Optionally fetching market data with yfinance
- Calculating daily and cumulative returns
- Measuring annualised volatility and drawdown
- Applying portfolio weights
- Calculating 1-day historical Value at Risk
- Running a simple Monte Carlo simulation
- Displaying charts and summary metrics in Streamlit

## Data Format

The dashboard supports three data sources:

- Demo data from `data/sample_prices.csv`
- CSV upload
- Optional yfinance market data fetch

CSV upload is the most reliable option. Upload a CSV with these columns:

```text
Date,Ticker,Close
```

The included `data/sample_prices.csv` file is synthetic demo data. It is not real investment data.

For yfinance, the app includes preset groups for US mega-cap technology stocks, US banks, UK large caps, global ETFs, and a mixed demo portfolio. You can also edit the ticker list manually. The dashboard limits yfinance requests to a maximum of 8 tickers.

Market data is fetched using yfinance for educational and research purposes. yfinance is not affiliated with, endorsed by, or vetted by Yahoo. Data may be delayed, unavailable, or subject to Yahoo's terms of use. This dashboard does not provide investment advice.

## Assumptions And Limitations

- This project is for educational analysis only and is not investment advice.
- Historical VaR is calculated from daily portfolio returns.
- Monte Carlo paths are illustrative scenarios, not market forecasts.
- The simulation assumes normally distributed returns, constant mean and volatility, no transaction costs, and fixed portfolio weights.
- yfinance data may be delayed, unavailable for some tickers, or affected by Yahoo's terms of use.
- No advanced finance libraries are used.

## Project Structure

```text
portfolio-risk-dashboard/
|-- app.py
|-- data/
|   `-- sample_prices.csv
|-- src/
|   |-- charts.py
|   |-- data_loader.py
|   |-- metrics.py
|   |-- portfolio.py
|   `-- risk.py
|-- tests/
|   |-- test_charts.py
|   |-- test_data_loader.py
|   |-- test_metrics.py
|   |-- test_portfolio.py
|   `-- test_risk.py
|-- AGENTS.md
|-- PROJECT_BRIEF.md
|-- README.md
|-- TASKS.md
`-- requirements.txt
```

## How To Run

Install the project dependencies, then start the Streamlit app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

On Windows with the included virtual environment:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## How To Test

```bash
pytest
```

On Windows with the included virtual environment:

```powershell
.\.venv\Scripts\pytest.exe tests
```
