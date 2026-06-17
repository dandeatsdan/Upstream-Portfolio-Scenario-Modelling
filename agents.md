# Scenario Modeller Instructions

This project is an oil and gas portfolio planning scenario modeller.

Key principles:

- Calculation engine and UI must remain separate.
- Streamlit is the front end only.
- All calculations occur in Python modules.
- Auditability is critical.
- Every scenario must produce an audit trail.
- Baseline data must never be modified.
- Anchor year 2024 is locked.
- Scenario operations are configuration driven.

Coding standards:

- Use pandas.
- Use type hints where practical.
- Use functions rather than large scripts.
- Document major functions.
- Avoid hard-coded values.