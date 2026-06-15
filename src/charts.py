"""Chart creation helpers for the Portfolio Risk Dashboard."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter


CHART_COLORS = [
    "#2563eb",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#7c3aed",
    "#0891b2",
]


def _apply_clean_axis_style(axis):
    """Apply simple dashboard-friendly styling to a matplotlib axis."""
    axis.grid(True, linestyle="--", linewidth=0.6, alpha=0.28)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color("#d8dee9")
    axis.spines["bottom"].set_color("#d8dee9")
    axis.tick_params(colors="#4b5563", labelsize=9)
    axis.title.set_color("#111827")
    axis.xaxis.label.set_color("#4b5563")
    axis.yaxis.label.set_color("#4b5563")


def plot_cumulative_returns(cumulative_returns_df):
    """Plot cumulative returns to show total growth or loss over time.

    Cumulative returns show how much each asset or portfolio has gained or lost
    since the start of the selected period.
    """
    figure, axis = plt.subplots(figsize=(9, 4.6))
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    cumulative_returns_df.plot(ax=axis, linewidth=2.1, color=CHART_COLORS)
    axis.axhline(0, color="#9ca3af", linewidth=0.8)
    axis.set_title("Compounded Return Since Start")
    axis.set_xlabel("Date")
    axis.set_ylabel("Total return")
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    axis.legend(title="Series", frameon=False)
    _apply_clean_axis_style(axis)
    figure.tight_layout()

    return figure


def plot_drawdowns(drawdown_df):
    """Plot drawdowns to show falls from previous peaks.

    Drawdown charts help investors see when an asset or portfolio was below its
    previous highest value and how deep the decline became.
    """
    figure, axis = plt.subplots(figsize=(9, 4.6))
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    drawdown_df.plot(ax=axis, linewidth=2.0, color=CHART_COLORS)
    axis.axhline(0, color="#9ca3af", linewidth=0.8)
    axis.set_title("Drawdown From Previous Peak")
    axis.set_xlabel("Date")
    axis.set_ylabel("Fall from peak")
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    axis.legend(title="Series", frameon=False)
    _apply_clean_axis_style(axis)
    figure.tight_layout()

    return figure


def plot_correlation_matrix(returns_df):
    """Plot a correlation matrix to compare how asset returns move together.

    Correlation shows whether assets tend to rise and fall together. A simple
    matrix helps explain diversification across different tickers.
    """
    correlation_matrix = returns_df.corr()

    figure, axis = plt.subplots(figsize=(6.7, 5.6))
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    image = axis.imshow(correlation_matrix, cmap="Blues", vmin=-1, vmax=1)
    axis.set_title("Asset Return Correlations")
    axis.set_xticks(range(len(correlation_matrix.columns)))
    axis.set_yticks(range(len(correlation_matrix.index)))
    axis.set_xticklabels(correlation_matrix.columns)
    axis.set_yticklabels(correlation_matrix.index)
    axis.set_xlabel("Ticker")
    axis.set_ylabel("Ticker")
    axis.tick_params(axis="x", rotation=45)
    axis.tick_params(colors="#4b5563", labelsize=9)

    for row_index, row_label in enumerate(correlation_matrix.index):
        for column_index, column_label in enumerate(correlation_matrix.columns):
            value = correlation_matrix.loc[row_label, column_label]
            axis.text(
                column_index,
                row_index,
                f"{value:.2f}",
                color="#111827",
                ha="center",
                va="center",
            )

    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("Correlation")
    figure.tight_layout()

    return figure


def plot_monte_carlo_paths(simulation_df):
    """Plot Monte Carlo simulation paths for possible future portfolio values.

    Each line is one simulated future path. The chart shows a range of possible
    outcomes rather than a single forecast.
    """
    figure, axis = plt.subplots(figsize=(9, 4.6))
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    paths_to_plot = simulation_df.iloc[:, :100]
    paths_to_plot.plot(
        ax=axis,
        color="#2563eb",
        legend=False,
        linewidth=0.8,
        alpha=0.18,
    )
    simulation_df.median(axis=1).plot(
        ax=axis,
        color="#111827",
        linewidth=2.2,
    )
    axis.set_title("Monte Carlo Simulation: Possible Portfolio Values")
    axis.set_xlabel("Future day")
    axis.set_ylabel("Portfolio value")
    axis.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    _apply_clean_axis_style(axis)
    figure.tight_layout()

    return figure
