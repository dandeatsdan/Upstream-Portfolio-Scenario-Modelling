"""Core scenario engine."""
from __future__ import annotations

import pandas as pd
from .operations import OPERATION_FUNCTIONS


def run_scenario(baseline_financials: pd.DataFrame, operation_table: pd.DataFrame) -> pd.DataFrame:
    """Apply operation rules sequentially to a baseline financial dataset."""
    scenario = baseline_financials.copy()
    if operation_table.empty:
        scenario["Scenario"] = "Scenario"
        return scenario

    for _, rule in operation_table.iterrows():
        operation = rule.get("Operation", "NoChange")
        fn = OPERATION_FUNCTIONS.get(operation)
        if fn is None:
            raise ValueError(f"Unsupported operation: {operation}")

        params = rule.dropna().to_dict()
        scenario = fn(scenario, **params)

    scenario["Scenario"] = "Scenario"
    return scenario


def compare_to_baseline(baseline: pd.DataFrame, scenario: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["Year"]
    value_cols = ["Production", "Revenue", "OPEX", "CAPEX", "PreTaxCashflow"]
    b = baseline.groupby(group_cols, as_index=False)[value_cols].sum()
    s = scenario.groupby(group_cols, as_index=False)[value_cols].sum()
    out = b.merge(s, on="Year", suffixes=("_Baseline", "_Scenario"))
    for col in value_cols:
        out[f"{col}_Delta"] = out[f"{col}_Scenario"] - out[f"{col}_Baseline"]
    return out


def npv(df: pd.DataFrame, discount_rate: float = 0.10, base_year: int | None = None) -> float:
    base_year = int(base_year or df["Year"].min())
    annual = df.groupby("Year", as_index=False)["PreTaxCashflow"].sum()
    annual["DiscountFactor"] = 1 / ((1 + discount_rate) ** (annual["Year"] - base_year))
    return float((annual["PreTaxCashflow"] * annual["DiscountFactor"]).sum())
