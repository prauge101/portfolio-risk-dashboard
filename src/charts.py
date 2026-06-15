"""Chart creation helpers for the Portfolio Risk Dashboard."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter


CHART_COLORS = [
    "#2dd4bf",
    "#60a5fa",
    "#a78bfa",
    "#f97316",
    "#fb7185",
    "#facc15",
]
CHART_BACKGROUND = "#151515"
GRID_COLOR = "#2a2a2a"
TEXT_COLOR = "#f5f7fb"
MUTED_TEXT_COLOR = "#a3a3a3"
SPINE_COLOR = "#343434"

plt.rcParams.update(
    {
        "axes.facecolor": CHART_BACKGROUND,
        "axes.labelcolor": MUTED_TEXT_COLOR,
        "axes.titlecolor": TEXT_COLOR,
        "figure.facecolor": CHART_BACKGROUND,
        "savefig.facecolor": CHART_BACKGROUND,
        "savefig.edgecolor": CHART_BACKGROUND,
        "text.color": TEXT_COLOR,
        "xtick.color": MUTED_TEXT_COLOR,
        "ytick.color": MUTED_TEXT_COLOR,
    }
)


def _apply_clean_axis_style(axis):
    """Apply simple dashboard-friendly styling to a matplotlib axis."""
    axis.set_axisbelow(True)
    axis.set_facecolor(CHART_BACKGROUND)
    axis.grid(True, linestyle="--", linewidth=0.6, color=GRID_COLOR, alpha=0.75)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(SPINE_COLOR)
    axis.spines["bottom"].set_color(SPINE_COLOR)
    axis.tick_params(axis="both", colors=MUTED_TEXT_COLOR, labelsize=9)
    axis.title.set_color(TEXT_COLOR)
    axis.xaxis.label.set_color(MUTED_TEXT_COLOR)
    axis.yaxis.label.set_color(MUTED_TEXT_COLOR)
    axis.xaxis.get_offset_text().set_color(MUTED_TEXT_COLOR)
    axis.yaxis.get_offset_text().set_color(MUTED_TEXT_COLOR)

    for label in axis.get_xticklabels() + axis.get_yticklabels():
        label.set_color(MUTED_TEXT_COLOR)


def _style_legend(legend):
    """Style matplotlib legends for the dark dashboard theme."""
    if legend is None:
        return

    legend.get_frame().set_facecolor("#1f1f1f")
    legend.get_frame().set_edgecolor("#343434")
    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)
    title = legend.get_title()
    if title is not None:
        title.set_color(TEXT_COLOR)


def _style_colorbar(colorbar):
    """Style a matplotlib colorbar so it remains readable on dark charts."""
    colorbar.outline.set_edgecolor(SPINE_COLOR)
    colorbar.ax.set_facecolor(CHART_BACKGROUND)
    colorbar.ax.tick_params(colors=MUTED_TEXT_COLOR, labelsize=9)
    colorbar.ax.yaxis.label.set_color(MUTED_TEXT_COLOR)
    colorbar.ax.yaxis.get_offset_text().set_color(MUTED_TEXT_COLOR)

    for label in colorbar.ax.get_yticklabels():
        label.set_color(MUTED_TEXT_COLOR)


def _create_dark_figure(width: float = 9, height: float = 4.6):
    """Create a matplotlib figure and axis using the dashboard dark surface."""
    figure, axis = plt.subplots(figsize=(width, height))
    figure.patch.set_facecolor(CHART_BACKGROUND)
    figure.patch.set_alpha(1.0)
    axis.set_facecolor(CHART_BACKGROUND)

    return figure, axis


def _finish_dark_figure(figure, axis):
    """Keep all visible matplotlib text readable on the dark dashboard theme."""
    _apply_clean_axis_style(axis)
    figure.tight_layout()


def plot_cumulative_returns(cumulative_returns_df):
    """Plot cumulative returns to show total growth or loss over time.

    Cumulative returns show how much each asset or portfolio has gained or lost
    since the start of the selected period.
    """
    figure, axis = _create_dark_figure()
    cumulative_returns_df.plot(ax=axis, linewidth=2.1, color=CHART_COLORS)
    axis.axhline(0, color="#64748b", linewidth=0.8)
    axis.set_title("Compounded Return Since Start")
    axis.set_xlabel("Date")
    axis.set_ylabel("Total return")
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    _style_legend(axis.legend(title="Series", frameon=False))
    _finish_dark_figure(figure, axis)

    return figure


def plot_drawdowns(drawdown_df):
    """Plot drawdowns to show falls from previous peaks.

    Drawdown charts help investors see when an asset or portfolio was below its
    previous highest value and how deep the decline became.
    """
    figure, axis = _create_dark_figure()
    drawdown_df.plot(ax=axis, linewidth=2.0, color=CHART_COLORS)
    axis.axhline(0, color="#64748b", linewidth=0.8)
    axis.set_title("Drawdown From Previous Peak")
    axis.set_xlabel("Date")
    axis.set_ylabel("Fall from peak")
    axis.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    _style_legend(axis.legend(title="Series", frameon=False))
    _finish_dark_figure(figure, axis)

    return figure


def plot_correlation_matrix(returns_df):
    """Plot a correlation matrix to compare how asset returns move together.

    Correlation shows whether assets tend to rise and fall together. A simple
    matrix helps explain diversification across different tickers.
    """
    correlation_matrix = returns_df.corr()

    figure, axis = _create_dark_figure(width=6.7, height=5.6)
    image = axis.imshow(correlation_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    axis.set_title("Asset Return Correlations")
    axis.set_xticks(range(len(correlation_matrix.columns)))
    axis.set_yticks(range(len(correlation_matrix.index)))
    axis.set_xticklabels(correlation_matrix.columns)
    axis.set_yticklabels(correlation_matrix.index)
    axis.set_xlabel("Ticker")
    axis.set_ylabel("Ticker")
    axis.tick_params(axis="x", rotation=45, colors=MUTED_TEXT_COLOR)

    for row_index, row_label in enumerate(correlation_matrix.index):
        for column_index, column_label in enumerate(correlation_matrix.columns):
            value = correlation_matrix.loc[row_label, column_label]
            axis.text(
                column_index,
                row_index,
                f"{value:.2f}",
                color="#f8fafc",
                ha="center",
                va="center",
            )

    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("Correlation")
    _style_colorbar(colorbar)
    _finish_dark_figure(figure, axis)

    return figure


def plot_monte_carlo_paths(simulation_df):
    """Plot Monte Carlo simulation paths for illustrative portfolio scenarios.

    The light lines show a small sample of scenarios. The dark line shows the
    median scenario, and the shaded band shows the 5th to 95th percentile range.
    The chart should be read as uncertainty analysis, not a forecast.
    """
    figure, axis = _create_dark_figure()
    paths_to_plot = simulation_df.iloc[:, :10]
    trading_days = simulation_df.index
    percentile_5 = simulation_df.quantile(0.05, axis=1)
    median_path = simulation_df.median(axis=1)
    percentile_95 = simulation_df.quantile(0.95, axis=1)

    percentile_band = axis.fill_between(
        trading_days,
        percentile_5.to_numpy(),
        percentile_95.to_numpy(),
        color="#2dd4bf",
        alpha=0.13,
        label="5th-95th percentile range",
    )

    for column in paths_to_plot.columns:
        axis.plot(
            trading_days,
            paths_to_plot[column].to_numpy(),
            color="#2dd4bf",
            linewidth=0.7,
            alpha=0.12,
            label="_nolegend_",
        )

    median_line = axis.plot(
        trading_days,
        median_path.to_numpy(),
        color="#f8fafc",
        label="Median simulated path",
        linewidth=2.2,
    )[0]

    axis.set_title("Monte Carlo risk simulation")
    axis.set_xlabel("Simulated trading days")
    axis.set_ylabel("Portfolio value")
    axis.yaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}"))
    _style_legend(
        axis.legend(
            handles=[percentile_band, median_line],
            labels=["5th-95th percentile range", "Median simulated path"],
            frameon=False,
        )
    )
    _finish_dark_figure(figure, axis)

    return figure
