"""Streamlit user interface for the Portfolio Risk Dashboard."""

import importlib
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
import src.risk as risk
from src.ui_components import inject_global_styles, kpi_card, page_header

risk = importlib.reload(risk)


YFINANCE_PRESETS = {
    "US Mega-Cap Tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "US Banks": ["JPM", "BAC", "GS", "MS", "C"],
    "UK Large Caps": ["SHEL.L", "BP.L", "HSBA.L", "RR.L", "TSCO.L"],
    "Global ETFs": ["SPY", "QQQ", "VTI", "EFA", "EEM"],
    "Mixed Demo Portfolio": ["AAPL", "MSFT", "JPM", "SHEL.L", "RR.L"],
}
YFINANCE_PERIODS = ["6mo", "1y", "2y", "5y"]
STRESS_SCENARIOS = {
    "Mild sell-off: all assets -5%": -0.05,
    "Market correction: all assets -10%": -0.10,
    "Severe shock: all assets -20%": -0.20,
    "Custom ticker shocks": None,
}
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


def ticker_chip_row(price_data, max_tickers: int = 8) -> None:
    """Render a compact row of latest ticker prices for dashboard context."""
    latest_prices = (
        price_data.sort_values("Date")
        .groupby("Ticker", as_index=False)
        .tail(1)
        .sort_values("Ticker")
        .head(max_tickers)
    )
    chips = []
    for _, row in latest_prices.iterrows():
        chips.append(
            '<div class="ticker-chip">'
            f'<span class="ticker-symbol">{escape(str(row["Ticker"]))}</span>'
            f'<span class="ticker-price">Close {row["Close"]:,.2f}</span>'
            "</div>"
        )

    st.markdown(
        f'<div class="ticker-strip">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def dark_table(data, max_rows: int | None = None) -> None:
    """Render a compact dark table that matches the dashboard theme."""
    table_data = data.copy()
    if max_rows is not None:
        table_data = table_data.head(max_rows)

    html_table = table_data.to_html(
        classes="dark-table",
        border=0,
        escape=True,
    )
    st.markdown(
        f'<div class="dark-table-wrap">{html_table}</div>',
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


_LEGACY_INLINE_STYLES = '''
st.markdown(
    """
    <style>
    .stApp {
        background: #edf2f7;
        color: #111827;
        color-scheme: light;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #111827;
    }

    .stApp p,
    .stApp label,
    .stApp span {
        color: #111827;
    }

    .stApp input,
    .stApp textarea,
    .stApp div[data-baseweb="input"],
    .stApp div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #cbd5e1 !important;
        color: #111827 !important;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #dbe3ef;
        color: #111827;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: #ffffff !important;
        border-color: #cbd5e1 !important;
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        color: #111827 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border-color: #dbe3ef;
        border-radius: 8px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stExpander"] {
        background: #ffffff;
        border-color: #dbe3ef;
    }

    div[data-testid="stExpander"] summary p {
        color: #111827 !important;
    }

    button[data-baseweb="tab"] p {
        color: #475569 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ef4444 !important;
        font-weight: 700;
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
        color: #93c5fd !important;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
    }

    .dashboard-hero h1 {
        color: #ffffff !important;
        font-size: 2.25rem;
        line-height: 1.15;
        margin: 0 0 0.45rem 0;
    }

    .dashboard-hero p {
        color: #dbeafe !important;
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
        color: #bfdbfe !important;
        font-size: 0.78rem;
        margin-bottom: 0.2rem;
    }

    .hero-pill-value {
        color: #ffffff !important;
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

    /* Reference-inspired dark finance dashboard overrides.
       The app uses one consistent dark theme so Streamlit's native
       light/dark toggle cannot leave mixed light panels behind. */
    html,
    body,
    #root {
        background: #0b0b0b !important;
        color-scheme: dark !important;
    }

    .stApp {
        background: #0b0b0b !important;
        color: #e5edf7 !important;
        color-scheme: dark;
    }

    header[data-testid="stHeader"],
    .stApp > header,
    .stAppHeader {
        background: #0b0b0b !important;
        border-bottom: 1px solid #1f1f1f !important;
    }

    header[data-testid="stHeader"] *,
    .stAppHeader * {
        background: transparent !important;
    }

    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {
        background: #0b0b0b !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #0b0b0b !important;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp p,
    .stApp label,
    .stApp span {
        color: #e5edf7 !important;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] {
        background: #101010 !important;
        border-right: 1px solid #2a2a2a !important;
        color: #e5edf7 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e5edf7 !important;
    }

    .stApp input,
    .stApp textarea,
    .stApp div[data-baseweb="input"],
    .stApp div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: #151515 !important;
        border-color: #343434 !important;
        color: #f8fafc !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"] {
        background: #151515 !important;
        border-color: #2a2a2a !important;
        border-radius: 8px !important;
        box-shadow: 0 16px 42px rgba(0, 0, 0, 0.28) !important;
    }

    div[data-testid="stExpander"] summary p {
        color: #f8fafc !important;
    }

    .dashboard-hero {
        background:
            radial-gradient(circle at 85% 20%, rgba(45, 212, 191, 0.22), transparent 34%),
            linear-gradient(135deg, #0b0b0b 0%, #151515 58%, #10211f 100%) !important;
        border: 1px solid #2a2a2a !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.36) !important;
    }

    .dashboard-eyebrow {
        color: #2dd4bf !important;
    }

    .dashboard-hero p {
        color: #c7c7c7 !important;
    }

    .hero-pill {
        background: rgba(21, 21, 21, 0.86) !important;
        border-color: #343434 !important;
    }

    .hero-pill-label {
        color: #a3a3a3 !important;
    }

    .hero-pill-value {
        color: #f8fafc !important;
    }

    .panel-title {
        color: #f8fafc !important;
    }

    .panel-note,
    .section-note,
    .risk-table-note,
    .metric-detail,
    div[data-testid="stMetricLabel"] p {
        color: #a3a3a3 !important;
    }

    .metric-card {
        background: #151515 !important;
        border-color: #2a2a2a !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.26) !important;
    }

    .metric-label {
        color: #a3a3a3 !important;
    }

    .metric-value {
        color: #f8fafc !important;
    }

    .metric-card-blue::before {
        background: #2dd4bf;
    }

    .metric-card-green::before {
        background: #34d399;
    }

    .metric-card-amber::before {
        background: #fbbf24;
    }

    .metric-card-red::before {
        background: #fb7185;
    }

    .metric-card-slate::before {
        background: #94a3b8;
    }

    button[data-baseweb="tab"] {
        background: #151515 !important;
        border-radius: 8px 8px 0 0 !important;
    }

    button[data-baseweb="tab"] p {
        color: #a3a3a3 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #2dd4bf !important;
        font-weight: 700;
    }

    .ticker-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 0.2rem 0 1.1rem 0;
    }

    .ticker-chip {
        align-items: center;
        background: #151515;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        display: inline-flex;
        gap: 0.65rem;
        padding: 0.62rem 0.78rem;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.18);
    }

    .ticker-symbol {
        color: #f8fafc !important;
        font-size: 0.86rem;
        font-weight: 800;
    }

    .ticker-price {
        color: #2dd4bf !important;
        font-size: 0.82rem;
    }

    div[data-testid="stAlert"] {
        background: #0b2138 !important;
        border-color: #1d4ed8 !important;
        color: #dbeafe !important;
    }

    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: #dbeafe !important;
    }

    div[data-testid="stDataFrame"] {
        background: #151515 !important;
        border-radius: 8px;
    }

    .dark-table-wrap {
        background: #151515;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        margin-top: 0.35rem;
        max-height: 360px;
        overflow: auto;
    }

    table.dark-table {
        border-collapse: collapse;
        color: #e5edf7;
        font-size: 0.86rem;
        width: 100%;
    }

    table.dark-table thead th {
        background: #1f1f1f;
        border-bottom: 1px solid #2a2a2a;
        color: #a3a3a3 !important;
        font-size: 0.74rem;
        font-weight: 800;
        padding: 0.65rem 0.75rem;
        text-align: left;
        text-transform: uppercase;
    }

    table.dark-table tbody th,
    table.dark-table tbody td {
        border-bottom: 1px solid #2a2a2a;
        color: #e5edf7 !important;
        padding: 0.58rem 0.75rem;
        text-align: left;
    }

    table.dark-table tbody tr:hover {
        background: #1f1f1f;
    }

    /* Final contrast pass: Material-style dark theme with clear elevation.
       Dark surfaces get lighter as they rise, while text uses stronger
       high/medium emphasis levels so controls stay readable. */
    html,
    body,
    #root,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #182030 !important;
        color: #f8fafc !important;
        color-scheme: dark !important;
    }

    header[data-testid="stHeader"],
    .stApp > header,
    .stAppHeader,
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {
        background: #182030 !important;
        border-bottom-color: #52647d !important;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #f8fafc !important;
    }

    .stApp p,
    .stApp label,
    .stApp span,
    .stApp li,
    .stApp small,
    [data-testid="stMarkdownContainer"] {
        color: #eef4fb !important;
    }

    [data-testid="stSidebar"] {
        background: #202a3a !important;
        border-right: 1px solid #52647d !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] small {
        color: #eef4fb !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label *,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label * {
        color: #eef4fb !important;
        opacity: 1 !important;
    }

    .stApp input,
    .stApp textarea,
    .stApp div[data-baseweb="input"],
    .stApp div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: #2f3b4f !important;
        border-color: #7b8ea8 !important;
        color: #f8fafc !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"] {
        background: #263244 !important;
        border: 1px solid #5f7189 !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18) !important;
    }

    div[data-testid="stExpander"] summary {
        background: #2f3b4f !important;
        border-bottom: 1px solid #5f7189 !important;
        border-radius: 8px 8px 0 0 !important;
    }

    div[data-testid="stExpander"] summary p {
        color: #f8fafc !important;
    }

    .dashboard-hero {
        background:
            radial-gradient(circle at 82% 18%, rgba(103, 232, 249, 0.24), transparent 34%),
            linear-gradient(135deg, #202a3a 0%, #263244 56%, #1e5f6f 100%) !important;
        border-color: #5f7189 !important;
    }

    .dashboard-hero p,
    .panel-note,
    .section-note,
    .risk-table-note,
    .metric-detail,
    div[data-testid="stMetricLabel"] p {
        color: #dce7f3 !important;
    }

    .dashboard-eyebrow,
    .ticker-price,
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #5eead4 !important;
    }

    .hero-pill,
    .metric-card,
    .ticker-chip {
        background: #2f3b4f !important;
        border: 1px solid #5f7189 !important;
    }

    .metric-label,
    .hero-pill-label {
        color: #dce7f3 !important;
    }

    .metric-value,
    .hero-pill-value,
    .ticker-symbol {
        color: #ffffff !important;
    }

    .dark-table-wrap {
        background: #263244 !important;
        border: 1px solid #7b8ea8 !important;
        box-shadow: inset 0 0 0 1px rgba(226, 232, 240, 0.14);
    }

    table.dark-table {
        color: #f8fafc !important;
        font-size: 0.88rem;
    }

    table.dark-table thead th {
        background: #202a3a !important;
        border-bottom: 2px solid #8fa3bd !important;
        color: #ffffff !important;
    }

    table.dark-table tbody tr:nth-child(odd) {
        background: #263244 !important;
    }

    table.dark-table tbody tr:nth-child(even) {
        background: #324056 !important;
    }

    table.dark-table tbody th,
    table.dark-table tbody td {
        border-bottom: 1px solid #71839b !important;
        border-right: 1px solid #52647d !important;
        color: #f8fafc !important;
    }

    table.dark-table tbody th {
        color: #e2e8f0 !important;
        font-weight: 700;
    }

    table.dark-table tbody tr:hover {
        background: #3c4b63 !important;
    }

    div[data-testid="stAlert"] {
        background: #17324f !important;
        border-color: #60a5fa !important;
    }

    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: #e0f2fe !important;
    }

    div[data-baseweb="radio"] label,
    div[data-baseweb="checkbox"] label {
        opacity: 1 !important;
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
'''

inject_global_styles()
page_header(
    "Portfolio Risk Dashboard",
    (
        "Analyse portfolio risk from price data using returns, volatility, "
        "drawdowns, correlations, historical Value at Risk, and a simple "
        "Monte Carlo simulation."
    ),
    [
        ("Input source", "CSV price data"),
        ("Risk view", "Returns, VaR and simulations"),
    ],
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
if not show_monte_carlo:
    st.sidebar.caption("Monte Carlo simulation is disabled.")

ticker_chip_row(price_data)

st.subheader("Dataset Overview")
data_col1, data_col2, data_col3, data_col4, data_col5 = st.columns(5)
with data_col1:
    kpi_card("Tickers", str(len(tickers)), "Assets detected", "blue")
with data_col2:
    kpi_card("Price Rows", f"{len(price_data):,}", "Raw observations", "slate")
with data_col3:
    kpi_card("Return Days", f"{len(daily_returns):,}", "Calculated periods", "green")
with data_col4:
    kpi_card("Start Date", format_date(price_data["Date"].min()), "First price", "amber")
with data_col5:
    kpi_card("End Date", format_date(price_data["Date"].max()), "Latest price", "red")

with st.expander("Raw price data preview", expanded=False):
    preview_data = price_data.head(20).copy()
    preview_data["Date"] = preview_data["Date"].dt.strftime("%Y-%m-%d")
    dark_table(preview_data)

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
            dark_table(volatility_table.map(format_percent).to_frame())

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
            dark_table(drawdown_table.map(format_percent).to_frame())

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
        historical_var = risk.calculate_historical_var(portfolio_returns)
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

        with st.container(border=True):
            st.subheader("Stress testing")
            st.markdown(
                '<p class="section-note">Stress testing shows how the portfolio '
                "would respond to hypothetical market shocks. It is not a "
                "prediction.</p>",
                unsafe_allow_html=True,
            )

            stress_col1, stress_col2 = st.columns([1, 1])
            with stress_col1:
                stress_scenario = st.selectbox(
                    "Stress scenario",
                    list(STRESS_SCENARIOS.keys()),
                )
            with stress_col2:
                stress_portfolio_value = st.number_input(
                    "Stress test portfolio value",
                    min_value=100.0,
                    value=10000.0,
                    step=500.0,
                    format="%.2f",
                )

            if STRESS_SCENARIOS[stress_scenario] is None:
                st.caption("Enter shocks as percentages. For example, -10 means -10%.")
                shocks = {}
                shock_columns = st.columns(min(4, len(tickers)))
                for index, ticker in enumerate(tickers):
                    with shock_columns[index % len(shock_columns)]:
                        shock_percent = st.number_input(
                            f"{ticker} shock (%)",
                            value=-10.0,
                            step=1.0,
                            format="%.2f",
                        )
                    shocks[ticker] = shock_percent / 100
            else:
                scenario_shock = STRESS_SCENARIOS[stress_scenario]
                shocks = {ticker: scenario_shock for ticker in tickers}

            try:
                stress_result = risk.calculate_stress_test_loss(
                    weights,
                    shocks,
                    portfolio_value=float(stress_portfolio_value),
                )
            except ValueError as error:
                st.error(str(error))
            else:
                stress_metric_col1, stress_metric_col2, stress_metric_col3 = st.columns(3)
                with stress_metric_col1:
                    metric_card(
                        "Portfolio impact",
                        format_percent(stress_result["portfolio_impact_percent"]),
                        "Weighted shock effect",
                        "red",
                    )
                with stress_metric_col2:
                    metric_card(
                        "Estimated value impact",
                        f"£{stress_result['portfolio_impact_value']:,.2f}",
                        "Change in portfolio value",
                        "amber",
                    )
                with stress_metric_col3:
                    metric_card(
                        "Stressed portfolio value",
                        f"£{stress_result['stressed_portfolio_value']:,.2f}",
                        "Value after scenario shock",
                        "blue",
                    )

        with st.expander("Monte Carlo risk simulation", expanded=False):
            if show_monte_carlo:
                st.markdown(
                    '<p class="section-note">This simulation uses historical mean '
                    "return and volatility to generate possible future paths. It "
                    "is a simplified uncertainty model, not a prediction of future "
                    "prices.</p>",
                    unsafe_allow_html=True,
                )

                control_col1, control_col2, control_col3 = st.columns(3)
                with control_col1:
                    num_simulations = st.number_input(
                        "Number of simulations",
                        min_value=100,
                        max_value=2000,
                        value=500,
                        step=100,
                    )
                with control_col2:
                    num_days = st.selectbox(
                        "Simulation horizon",
                        [30, 90, 252, 1260],
                        index=2,
                        format_func=lambda days: f"{days} trading days",
                    )
                with control_col3:
                    initial_value = st.number_input(
                        "Initial portfolio value",
                        min_value=100.0,
                        value=10000.0,
                        step=500.0,
                        format="%.2f",
                    )

                simulation_paths = risk.run_monte_carlo_simulation(
                    portfolio_returns,
                    num_simulations=int(num_simulations),
                    num_days=int(num_days),
                    initial_value=float(initial_value),
                )
                st.pyplot(plot_monte_carlo_paths(simulation_paths), clear_figure=True)
            else:
                st.info("Monte Carlo simulation is disabled in the sidebar.")

        with st.expander("Advanced correlated Monte Carlo", expanded=False):
            if show_monte_carlo:
                st.markdown(
                    '<p class="section-note">This model simulates assets jointly '
                    "using their historical covariance matrix, so it captures how "
                    "portfolio holdings may move together.</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p class="section-note">This is a simplified educational '
                    "model, not a forecast of future portfolio values.</p>",
                    unsafe_allow_html=True,
                )

                advanced_col1, advanced_col2, advanced_col3 = st.columns(3)
                with advanced_col1:
                    advanced_num_simulations = st.number_input(
                        "Advanced simulations",
                        min_value=100,
                        max_value=5000,
                        value=1000,
                        step=100,
                    )
                with advanced_col2:
                    advanced_num_days = st.selectbox(
                        "Advanced horizon",
                        [30, 90, 252, 1260],
                        index=2,
                        format_func=lambda days: f"{days} trading days",
                    )
                with advanced_col3:
                    advanced_initial_value = st.number_input(
                        "Advanced initial portfolio value",
                        min_value=100.0,
                        value=10000.0,
                        step=500.0,
                        format="%.2f",
                    )

                try:
                    correlated_simulation_paths = risk.run_correlated_monte_carlo_simulation(
                        daily_returns,
                        weights,
                        num_simulations=int(advanced_num_simulations),
                        num_days=int(advanced_num_days),
                        initial_value=float(advanced_initial_value),
                    )
                    simulation_summary = risk.calculate_simulation_summary(
                        correlated_simulation_paths,
                        initial_value=float(advanced_initial_value),
                    )
                except ValueError as error:
                    st.error(str(error))
                else:
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    with summary_col1:
                        metric_card(
                            "Median final value",
                            f"${simulation_summary['median_final_value']:,.2f}",
                            "Middle simulated ending value",
                            "blue",
                        )
                    with summary_col2:
                        metric_card(
                            "5th percentile final value",
                            f"${simulation_summary['percentile_5_final_value']:,.2f}",
                            "Downside final-value threshold",
                            "red",
                        )
                    with summary_col3:
                        metric_card(
                            "95th percentile final value",
                            f"${simulation_summary['percentile_95_final_value']:,.2f}",
                            "Upside final-value threshold",
                            "green",
                        )

                    risk_col1, risk_col2, risk_col3 = st.columns(3)
                    with risk_col1:
                        metric_card(
                            "Probability of loss",
                            format_percent(simulation_summary["probability_of_loss"]),
                            "Share ending below initial value",
                            "amber",
                        )
                    with risk_col2:
                        metric_card(
                            "Simulated VaR",
                            f"${simulation_summary['simulated_var']:,.2f}",
                            "Loss at the 5th percentile final value",
                            "red",
                        )
                    with risk_col3:
                        metric_card(
                            "Expected Shortfall",
                            f"${simulation_summary['expected_shortfall']:,.2f}",
                            "Average loss in the worst 5% of outcomes",
                            "slate",
                        )

                    st.pyplot(
                        plot_monte_carlo_paths(correlated_simulation_paths),
                        clear_figure=True,
                    )
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
