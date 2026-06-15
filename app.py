"""Streamlit user interface for the Portfolio Risk Dashboard."""

from html import escape

import streamlit as st

from src.charts import (
    plot_correlation_matrix,
    plot_cumulative_returns,
    plot_drawdowns,
    plot_monte_carlo_paths,
)
from src.data_loader import (
    MAX_YFINANCE_TICKERS,
    fetch_yfinance_price_data,
    load_price_data,
    parse_ticker_list,
)
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


YFINANCE_PRESETS = {
    "US Mega-Cap Tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "US Banks": ["JPM", "BAC", "GS", "MS", "C"],
    "UK Large Caps": ["SHEL.L", "BP.L", "HSBA.L", "RR.L", "TSCO.L"],
    "Global ETFs": ["SPY", "QQQ", "VTI", "EFA", "EEM"],
    "Mixed Demo Portfolio": ["AAPL", "MSFT", "JPM", "SHEL.L", "RR.L"],
}
YFINANCE_PERIODS = ["6mo", "1y", "2y", "5y"]
YFINANCE_DISCLAIMER = (
    "Market data is fetched using yfinance for educational and research "
    "purposes. yfinance is not affiliated with, endorsed by, or vetted by "
    "Yahoo. Data may be delayed, unavailable, or subject to Yahoo's terms of "
    "use. This dashboard does not provide investment advice."
)


st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide",
)


def format_percent(value: float) -> str:
    """Format decimal returns and risk values as percentages for the UI."""
    return f"{value:.2%}"


def format_date(value) -> str:
    """Format a pandas timestamp for compact dashboard display."""
    return value.strftime("%d %b %Y")


def metric_card(label: str, value: str, detail: str = "", tone: str = "blue") -> None:
    """Render a compact dashboard metric card."""
    st.markdown(
        f"""
        <div class="metric-card metric-card-{escape(tone)}">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-detail">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch_yfinance_price_data(
    tickers: tuple[str, ...],
    period: str,
    interval: str,
):
    """Fetch yfinance data through Streamlit's cache to reduce repeat calls."""
    return fetch_yfinance_price_data(list(tickers), period=period, interval=interval)


st.markdown(
    """
    <style>
    .stApp {
        background: #edf2f7;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #dbe3ef;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #111827;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #dbe3ef;
        border-radius: 8px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
    }

    .dashboard-hero {
        background: linear-gradient(135deg, #111827 0%, #1f3a5f 58%, #2563eb 100%);
        border: 1px solid #1f2937;
        border-radius: 8px;
        box-shadow: 0 18px 42px rgba(15, 23, 42, 0.18);
        color: #ffffff;
        display: grid;
        gap: 1.25rem;
        grid-template-columns: minmax(0, 1.7fr) minmax(260px, 0.9fr);
        padding: 1.55rem 1.65rem;
        margin-bottom: 1.1rem;
    }

    .dashboard-eyebrow {
        color: #93c5fd;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
    }

    .dashboard-hero h1 {
        color: #ffffff;
        font-size: 2.25rem;
        line-height: 1.15;
        margin: 0 0 0.45rem 0;
    }

    .dashboard-hero p {
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.55;
        margin: 0;
        max-width: 780px;
    }

    .hero-side {
        align-content: center;
        display: grid;
        gap: 0.65rem;
    }

    .hero-pill {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
    }

    .hero-pill-label {
        color: #bfdbfe;
        font-size: 0.78rem;
        margin-bottom: 0.2rem;
    }

    .hero-pill-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .upload-panel {
        background: #ffffff;
        border: 1px solid #dbe3ef;
        border-radius: 8px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        margin-bottom: 1rem;
        padding: 1rem 1.1rem 0.25rem 1.1rem;
    }

    .panel-title {
        color: #111827;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }

    .panel-note {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    .section-note {
        color: #6b7280;
        font-size: 0.92rem;
        margin-top: -0.35rem;
        margin-bottom: 0.9rem;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #dbe3ef;
        border-radius: 8px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        min-height: 118px;
        padding: 1rem 1rem 0.9rem 1rem;
        position: relative;
    }

    .metric-card::before {
        border-radius: 8px 0 0 8px;
        content: "";
        height: 100%;
        left: 0;
        position: absolute;
        top: 0;
        width: 4px;
    }

    .metric-card-blue::before {
        background: #2563eb;
    }

    .metric-card-green::before {
        background: #10b981;
    }

    .metric-card-amber::before {
        background: #f59e0b;
    }

    .metric-card-red::before {
        background: #ef4444;
    }

    .metric-card-slate::before {
        background: #475569;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.42rem;
        text-transform: uppercase;
    }

    .metric-value {
        color: #111827;
        font-size: 1.7rem;
        font-weight: 760;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .metric-detail {
        color: #64748b;
        font-size: 0.86rem;
        line-height: 1.35;
        margin-top: 0.45rem;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dbe3ef;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetricLabel"] p {
        color: #6b7280;
        font-size: 0.86rem;
    }

    .risk-table-note {
        color: #6b7280;
        font-size: 0.92rem;
        line-height: 1.4;
        min-height: 2.7rem;
        margin-top: -0.35rem;
        margin-bottom: 0.8rem;
    }

    @media (max-width: 900px) {
        .dashboard-hero {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-hero">
        <div>
            <div class="dashboard-eyebrow">Risk analytics project</div>
            <h1>Portfolio Risk Dashboard</h1>
            <p>
                Analyse portfolio risk from price data using returns, volatility,
                drawdowns, correlations, historical Value at Risk, and a simple
                Monte Carlo simulation.
            </p>
        </div>
        <div class="hero-side">
            <div class="hero-pill">
                <div class="hero-pill-label">Input source</div>
                <div class="hero-pill-value">CSV price data</div>
            </div>
            <div class="hero-pill">
                <div class="hero-pill-label">Risk view</div>
                <div class="hero-pill-value">Returns, VaR and simulations</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Portfolio Setup")
st.sidebar.header("Data Source")
data_source = st.sidebar.radio(
    "Choose price data source",
    ["Demo data", "Upload CSV", "Fetch market data with yfinance"],
)

uploaded_file = None
yfinance_tickers = []
yfinance_period = "2y"

if data_source == "Demo data":
    st.sidebar.caption("Uses synthetic sample data included in the project.")
elif data_source == "Upload CSV":
    st.sidebar.caption("CSV upload is the most reliable option.")
    uploaded_file = st.sidebar.file_uploader(
        "Upload price data CSV",
        type=["csv"],
        help="CSV must contain Date, Ticker, and Close columns.",
    )
else:
    st.sidebar.info(
        "Market data is fetched using yfinance for educational use. It may be "
        "delayed or unavailable for some tickers."
    )
    preset_name = st.sidebar.selectbox(
        "Preset ticker group",
        list(YFINANCE_PRESETS.keys()),
        index=4,
    )
    preset_tickers = ", ".join(YFINANCE_PRESETS[preset_name])
    ticker_text = st.sidebar.text_area(
        "Tickers",
        value=preset_tickers,
        key=f"yfinance_tickers_{preset_name}",
        help="Enter ticker symbols separated by commas.",
    )
    yfinance_period = st.sidebar.selectbox(
        "History period",
        YFINANCE_PERIODS,
        index=2,
    )

    try:
        entered_tickers = parse_ticker_list(ticker_text)
        if len(entered_tickers) > MAX_YFINANCE_TICKERS:
            st.sidebar.warning(
                f"Only the first {MAX_YFINANCE_TICKERS} tickers will be used. "
                f"You entered {len(entered_tickers)}."
            )
        yfinance_tickers = entered_tickers[:MAX_YFINANCE_TICKERS]
    except ValueError as error:
        st.sidebar.error(str(error))

with st.container(border=True):
    st.markdown('<div class="panel-title">Data Source</div>', unsafe_allow_html=True)
    if data_source == "Demo data":
        st.markdown(
            '<div class="panel-note">Using synthetic demo data from '
            "<code>data/sample_prices.csv</code>.</div>",
            unsafe_allow_html=True,
        )
    elif data_source == "Upload CSV":
        st.markdown(
            '<div class="panel-note">Upload a CSV with Date, Ticker and Close '
            "columns. This is the most reliable option.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="panel-note">Fetching adjusted daily close prices where '
            "available using yfinance.</div>",
            unsafe_allow_html=True,
        )
        st.caption(YFINANCE_DISCLAIMER)

try:
    if data_source == "Demo data":
        st.info(
            "Demo mode: using synthetic sample data from "
            "`data/sample_prices.csv`. Upload your own CSV to replace it."
        )
        price_data = load_price_data("data/sample_prices.csv")
    elif data_source == "Upload CSV":
        if uploaded_file is None:
            st.warning("Upload a CSV file to continue, or select demo data.")
            st.stop()
        st.success(f"Loaded uploaded file: `{uploaded_file.name}`.")
        price_data = load_price_data(uploaded_file)
    else:
        if not yfinance_tickers:
            st.warning("Enter at least one ticker to fetch market data.")
            st.stop()
        with st.spinner("Fetching market data with yfinance..."):
            price_data = cached_fetch_yfinance_price_data(
                tuple(yfinance_tickers),
                yfinance_period,
                "1d",
            )
        returned_tickers = set(price_data["Ticker"].unique())
        missing_tickers = [
            ticker for ticker in yfinance_tickers if ticker not in returned_tickers
        ]
        if missing_tickers:
            missing = ", ".join(missing_tickers)
            st.warning(f"No usable price data was returned for: {missing}")
        st.success(
            "Loaded yfinance market data for: "
            f"{', '.join(sorted(returned_tickers))}"
        )
except ValueError as error:
    st.error(str(error))
    st.stop()

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

st.sidebar.divider()
st.sidebar.header("Portfolio Weights")
st.sidebar.caption("Set weights as decimals. The default is an equal-weight portfolio.")

weights = {}
with st.sidebar.expander("Asset weights", expanded=True):
    for ticker in tickers:
        weights[ticker] = st.number_input(
            f"{ticker}",
            min_value=0.0,
            max_value=1.0,
            value=float(equal_weight),
            step=0.01,
            format="%.4f",
        )

    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) <= 0.000001:
        st.success(f"Total weight: {total_weight:.4f}")
    else:
        st.error(f"Total weight: {total_weight:.4f}. It must equal 1.0000.")

st.sidebar.divider()
st.sidebar.subheader("Monte Carlo Settings")
show_monte_carlo = st.sidebar.checkbox(
    "Show Monte Carlo simulation",
    value=True,
    help="Turn this off if you only want historical portfolio risk metrics.",
)
if show_monte_carlo:
    num_simulations = st.sidebar.number_input(
        "Simulation paths",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
    )
    num_days = st.sidebar.number_input(
        "Future days",
        min_value=1,
        max_value=1000,
        value=252,
        step=21,
    )
    initial_value = st.sidebar.number_input(
        "Initial portfolio value",
        min_value=100.0,
        value=10000.0,
        step=500.0,
        format="%.2f",
    )
else:
    st.sidebar.caption("Monte Carlo simulation is disabled.")

st.subheader("Dataset Overview")
data_col1, data_col2, data_col3, data_col4, data_col5 = st.columns(5)
with data_col1:
    metric_card("Tickers", str(len(tickers)), "Assets detected", "blue")
with data_col2:
    metric_card("Price Rows", f"{len(price_data):,}", "Raw observations", "slate")
with data_col3:
    metric_card("Return Days", f"{len(daily_returns):,}", "Calculated periods", "green")
with data_col4:
    metric_card("Start Date", format_date(price_data["Date"].min()), "First price", "amber")
with data_col5:
    metric_card("End Date", format_date(price_data["Date"].max()), "Latest price", "red")

with st.expander("Raw price data preview", expanded=True):
    st.dataframe(price_data.head(20), use_container_width=True)

asset_tab, portfolio_tab = st.tabs(["Asset Risk", "Portfolio Analysis"])

with asset_tab:
    with st.container(border=True):
        st.subheader("Asset Return Performance")
        st.markdown(
            '<p class="section-note">Compounded returns show how each ticker has '
            "grown or fallen since the first return date.</p>",
            unsafe_allow_html=True,
        )
        st.pyplot(plot_cumulative_returns(cumulative_returns), clear_figure=True)

    left_col, right_col = st.columns([1, 1])

    with left_col:
        with st.container(border=True):
            st.subheader("Annualised Volatility")
            st.markdown(
                '<p class="risk-table-note">Higher volatility means larger historical '
                "ups and downs in daily returns.</p>",
                unsafe_allow_html=True,
            )
            annualised_volatility = calculate_annualised_volatility(daily_returns)
            volatility_table = annualised_volatility.rename_axis("Ticker").rename("Value")
            st.dataframe(
                volatility_table.to_frame().style.format("{:.2%}"),
                use_container_width=True,
                height=170,
            )

    with right_col:
        with st.container(border=True):
            st.subheader("Maximum Drawdown")
            st.markdown(
                '<p class="risk-table-note">Maximum drawdown is the worst fall from a '
                "previous peak during the selected period.</p>",
                unsafe_allow_html=True,
            )
            max_drawdown = calculate_max_drawdown(cumulative_returns)
            drawdown_table = max_drawdown.rename_axis("Ticker").rename("Value")
            st.dataframe(
                drawdown_table.to_frame().style.format("{:.2%}"),
                use_container_width=True,
                height=170,
            )

    drawdowns = calculate_drawdown(cumulative_returns)

    with st.container(border=True):
        st.subheader("Drawdown History")
        st.markdown(
            '<p class="section-note">This chart shows when each ticker was below '
            "its previous high and how deep the decline became.</p>",
            unsafe_allow_html=True,
        )
        st.pyplot(plot_drawdowns(drawdowns), clear_figure=True)

    with st.container(border=True):
        st.subheader("Return Correlations")
        st.markdown(
            '<p class="section-note">Correlation helps show whether tickers tend '
            "to move together or provide diversification.</p>",
            unsafe_allow_html=True,
        )
        st.pyplot(plot_correlation_matrix(daily_returns), clear_figure=True)

with portfolio_tab:
    st.subheader("Portfolio Results")
    st.markdown(
        '<p class="section-note">Portfolio results use the sidebar weights and '
        "combine each ticker's daily return into one weighted portfolio.</p>",
        unsafe_allow_html=True,
    )

    try:
        validate_weights(weights, tickers)
        portfolio_returns = calculate_portfolio_returns(daily_returns, weights)
        portfolio_cumulative_returns = calculate_portfolio_cumulative_returns(
            portfolio_returns
        )
        historical_var = calculate_historical_var(portfolio_returns)
        if show_monte_carlo:
            simulation_paths = run_monte_carlo_simulation(
                portfolio_returns,
                num_simulations=int(num_simulations),
                num_days=int(num_days),
                initial_value=float(initial_value),
            )
    except ValueError as error:
        st.error(str(error))
    else:
        portfolio_volatility = calculate_annualised_volatility(
            portfolio_returns.to_frame()
        ).iloc[0]
        portfolio_max_drawdown = calculate_max_drawdown(
            portfolio_cumulative_returns.to_frame()
        ).iloc[0]
        final_cumulative_return = portfolio_cumulative_returns.iloc[-1]

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            metric_card(
                "Cumulative Return",
                format_percent(final_cumulative_return),
                "Weighted portfolio result",
                "green",
            )
        with metric_col2:
            metric_card(
                "Historical VaR (95%, 1-day)",
                format_percent(historical_var),
                "5th percentile daily portfolio loss",
                "red",
            )
        with metric_col3:
            metric_card(
                "Annualised Volatility",
                format_percent(portfolio_volatility),
                "Annualised from daily returns using 252 trading days",
                "amber",
            )
        with metric_col4:
            metric_card(
                "Max Drawdown",
                format_percent(portfolio_max_drawdown),
                "Worst peak-to-trough fall",
                "blue",
            )

        with st.container(border=True):
            st.subheader("Portfolio Cumulative Return")
            st.markdown(
                '<p class="section-note">This chart shows the compounded result of '
                "the weighted portfolio over the available history.</p>",
                unsafe_allow_html=True,
            )
            st.pyplot(
                plot_cumulative_returns(portfolio_cumulative_returns.to_frame()),
                clear_figure=True,
            )

        if show_monte_carlo:
            with st.container(border=True):
                st.subheader("Monte Carlo Simulation")
                st.markdown(
                    '<p class="section-note">The simulation uses historical average '
                    "return and volatility to generate illustrative scenarios. It "
                    "is not a market forecast.</p>",
                    unsafe_allow_html=True,
                )
                st.pyplot(plot_monte_carlo_paths(simulation_paths), clear_figure=True)
        else:
            st.info("Monte Carlo simulation is disabled in the sidebar.")

        with st.expander("Assumptions and limitations"):
            st.write(
                "This dashboard is for educational analysis only and is not "
                "investment advice. Historical VaR is based on daily portfolio "
                "returns. Monte Carlo paths assume normally distributed returns, "
                "constant mean and volatility, no transaction costs, and fixed "
                "portfolio weights over the simulated period."
            )
