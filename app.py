"""Streamlit user interface for the Portfolio Risk Dashboard."""

import streamlit as st

from src.charts import (
    plot_correlation_matrix,
    plot_cumulative_returns,
    plot_drawdowns,
    plot_monte_carlo_paths,
)
from src.data_loader import load_price_data
from src.metrics import (
    calculate_annualised_volatility,
    calculate_cumulative_returns,
    calculate_daily_returns,
    calculate_drawdown,
    calculate_max_drawdown,
)
from src.portfolio import (
    calculate_portfolio_cumulative_returns,
    calculate_portfolio_returns,
    validate_weights,
)
from src.risk import calculate_historical_var, run_monte_carlo_simulation


st.title("Portfolio Risk Dashboard")
st.write(
    "This dashboard analyses portfolio risk using stock price data. Upload a "
    "CSV file, or use the demo dataset to explore returns, volatility, "
    "drawdowns, Value at Risk, and Monte Carlo simulations."
)

uploaded_file = st.file_uploader(
    "Upload price data CSV",
    type=["csv"],
    help="CSV must contain Date, Ticker, and Close columns.",
)

try:
    if uploaded_file is None:
        st.info("Using demo data from data/sample_prices.csv.")
        price_data = load_price_data("data/sample_prices.csv")
    else:
        price_data = load_price_data(uploaded_file)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.subheader("Price Data Preview")
st.dataframe(price_data.head(20), use_container_width=True)

try:
    daily_returns = calculate_daily_returns(price_data)
    cumulative_returns = calculate_cumulative_returns(daily_returns)
except ValueError as error:
    st.error(str(error))
    st.stop()

if daily_returns.empty:
    st.error("At least two price dates are needed to calculate returns.")
    st.stop()

tickers = list(daily_returns.columns)
equal_weight = 1 / len(tickers)

st.sidebar.header("Portfolio Weights")
st.sidebar.write("Weights should add up to 1.00, or 100% of the portfolio.")

weights = {}
for ticker in tickers:
    weights[ticker] = st.sidebar.number_input(
        f"{ticker} weight",
        min_value=0.0,
        max_value=1.0,
        value=float(equal_weight),
        step=0.05,
        format="%.4f",
    )

st.sidebar.write(f"Current total weight: {sum(weights.values()):.4f}")

st.subheader("Cumulative Returns")
st.pyplot(plot_cumulative_returns(cumulative_returns))

st.subheader("Annualised Volatility")
annualised_volatility = calculate_annualised_volatility(daily_returns)
st.dataframe(
    annualised_volatility.rename("Annualised Volatility").to_frame(),
    use_container_width=True,
)

drawdowns = calculate_drawdown(cumulative_returns)

st.subheader("Drawdowns")
st.pyplot(plot_drawdowns(drawdowns))

st.subheader("Maximum Drawdown")
max_drawdown = calculate_max_drawdown(cumulative_returns)
st.dataframe(max_drawdown.rename("Maximum Drawdown").to_frame(), use_container_width=True)

st.subheader("Correlation Matrix")
st.pyplot(plot_correlation_matrix(daily_returns))

st.subheader("Portfolio Results")

try:
    validate_weights(weights, tickers)
    portfolio_returns = calculate_portfolio_returns(daily_returns, weights)
    portfolio_cumulative_returns = calculate_portfolio_cumulative_returns(
        portfolio_returns
    )
    historical_var = calculate_historical_var(portfolio_returns)
    simulation_paths = run_monte_carlo_simulation(portfolio_returns)
except ValueError as error:
    st.error(str(error))
    st.stop()

final_cumulative_return = portfolio_cumulative_returns.iloc[-1]

col1, col2 = st.columns(2)
col1.metric("Portfolio Cumulative Return", f"{final_cumulative_return:.2%}")
col2.metric("Historical VaR (95%)", f"{historical_var:.2%}")

st.pyplot(plot_cumulative_returns(portfolio_cumulative_returns.to_frame()))

st.subheader("Monte Carlo Simulation")
st.pyplot(plot_monte_carlo_paths(simulation_paths))
