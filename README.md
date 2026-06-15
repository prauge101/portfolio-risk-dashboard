# Portfolio Risk Dashboard

A beginner-friendly Python and Streamlit dashboard for analysing portfolio risk using stock price data.

This project is designed for a Mechanical Engineering student transitioning into finance, fintech, risk analytics, and consulting. The goal is to build a clean, explainable project that demonstrates Python, data analysis, finance concepts, and testing.

## Current Status

This repository currently contains the project scaffold only. Full finance logic and dashboard features will be added in later stages.

## Planned Features

- Load stock price data from CSV
- Calculate daily and cumulative returns
- Measure volatility and drawdown
- Apply portfolio weights
- Calculate historical Value at Risk
- Run a simple Monte Carlo simulation
- Display charts in Streamlit

## Project Structure

```text
portfolio-risk-dashboard/
├── app.py
├── data/
│   └── sample_prices.csv
├── src/
│   ├── charts.py
│   ├── data_loader.py
│   ├── metrics.py
│   ├── portfolio.py
│   └── risk.py
├── tests/
│   ├── test_metrics.py
│   ├── test_portfolio.py
│   └── test_risk.py
├── AGENTS.md
├── PROJECT_BRIEF.md
├── README.md
├── TASKS.md
└── requirements.txt
```

## How To Run

Install the project dependencies, then start the Streamlit app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How To Test

```bash
pytest
```
