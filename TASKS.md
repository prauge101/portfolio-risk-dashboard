# Tasks

## Staged MVP Roadmap

1. Project scaffold
   - Create the initial files and folders.
   - Add basic documentation and sample data.

2. Data loading
   - Load CSV price data.
   - Validate required columns: `Date`, `Ticker`, and `Close`.
   - Convert dates into a proper datetime format.

3. Daily and cumulative returns
   - Calculate daily percentage returns.
   - Calculate cumulative returns to show growth over time.

4. Volatility and drawdown
   - Calculate volatility as a measure of return variability.
   - Calculate drawdown to show declines from previous peaks.

5. Portfolio weights
   - Allow the user to assign weights to each ticker.
   - Calculate weighted portfolio returns.

6. Historical Value at Risk
   - Estimate Value at Risk using historical portfolio returns.
   - Explain what the result means in simple language.

7. Monte Carlo simulation
   - Simulate possible future portfolio paths.
   - Keep assumptions simple and clearly commented.

8. Chart functions
   - Create reusable chart functions with matplotlib.
   - Keep chart logic outside `app.py`.

9. Streamlit dashboard UI
   - Add file upload or sample data selection.
   - Add controls for tickers, weights, and risk settings.
   - Display results and charts clearly.

10. README polish and screenshots
    - Explain how to install and run the project.
    - Add screenshots of the finished dashboard.
    - Describe the project in CV-friendly language.
