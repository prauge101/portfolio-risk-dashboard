"""Chart creation helpers for the Portfolio Risk Dashboard."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def plot_cumulative_returns(cumulative_returns_df):
    """Plot cumulative returns to show total growth or loss over time.

    Cumulative returns show how much each asset or portfolio has gained or lost
    since the start of the selected period.
    """
    figure, axis = plt.subplots()
    cumulative_returns_df.plot(ax=axis)
    axis.set_title("Cumulative Returns")
    axis.set_xlabel("Date")
    axis.set_ylabel("Cumulative Return")
    axis.legend(title="Ticker")
    figure.tight_layout()

    return figure


def plot_drawdowns(drawdown_df):
    """Plot drawdowns to show falls from previous peaks.

    Drawdown charts help investors see when an asset or portfolio was below its
    previous highest value and how deep the decline became.
    """
    figure, axis = plt.subplots()
    drawdown_df.plot(ax=axis)
    axis.set_title("Drawdowns")
    axis.set_xlabel("Date")
    axis.set_ylabel("Drawdown")
    axis.legend(title="Ticker")
    figure.tight_layout()

    return figure


def plot_correlation_matrix(returns_df):
    """Plot a correlation matrix to compare how asset returns move together.

    Correlation shows whether assets tend to rise and fall together. A simple
    matrix helps explain diversification across different tickers.
    """
    correlation_matrix = returns_df.corr()

    figure, axis = plt.subplots()
    image = axis.imshow(correlation_matrix)
    axis.set_title("Return Correlation Matrix")
    axis.set_xticks(range(len(correlation_matrix.columns)))
    axis.set_yticks(range(len(correlation_matrix.index)))
    axis.set_xticklabels(correlation_matrix.columns)
    axis.set_yticklabels(correlation_matrix.index)
    figure.colorbar(image, ax=axis)
    figure.tight_layout()

    return figure


def plot_monte_carlo_paths(simulation_df):
    """Plot Monte Carlo simulation paths for possible future portfolio values.

    Each line is one simulated future path. The chart shows a range of possible
    outcomes rather than a single forecast.
    """
    figure, axis = plt.subplots()
    simulation_df.plot(ax=axis, legend=False)
    axis.set_title("Monte Carlo Simulation Paths")
    axis.set_xlabel("Day")
    axis.set_ylabel("Portfolio Value")
    figure.tight_layout()

    return figure
