# AGENTS.md

Guidance for future Codex sessions working on this Portfolio Risk Dashboard.

## Working Style

- Do not rewrite the whole app.
- Work on one feature at a time.
- State which files will be edited before making large changes.
- Keep changes small, readable, and easy to explain.
- Prefer simple Python over clever abstractions.

## Project Rules

- Use Python, pandas, numpy, matplotlib, Streamlit, and pytest.
- Keep calculation logic separate from the Streamlit UI.
- `app.py` should only handle the user interface.
- Core calculations should live in `src/`.
- Tests should live in `tests/`.
- Add tests for calculation functions.
- Add docstrings to every function.
- Add comments that clearly explain finance concepts.
- Do not use advanced finance libraries.
- Do not add live stock APIs yet.
- Start with CSV and sample data only.

## Interview Readiness

Keep the code simple enough that the project owner can explain it clearly in an internship interview. When adding a feature, make the financial idea, the Python implementation, and the testing approach easy to describe.
