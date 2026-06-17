"""Scenario operation functions.

These functions deliberately accept and return pandas DataFrames so that the
operation layer remains independent of Streamlit. This makes the engine easier
to test, reuse, and later move behind an API if required.
"""
from __future__ import annotations

import pandas as pd


VALUE_COLUMNS = ["Production", "Revenue", "OPEX", "CAPEX", "PreTaxCashflow"]


def _case_mask(df: pd.DataFrame, case_id: str, effective_year: int | None = None) -> pd.Series:
    mask = df["CaseID"].eq(case_id)
    if effective_year is not None:
        mask = mask & df["Year"].ge(int(effective_year))
    return mask


def apply_exclude(df: pd.DataFrame, case_id: str, effective_year: int = 2026, **_: object) -> pd.DataFrame:
    out = df.copy()
    mask = _case_mask(out, case_id, effective_year)
    out.loc[mask, VALUE_COLUMNS] = 0
    return out


def apply_delay(df: pd.DataFrame, case_id: str, effective_year: int, delay_years: int = 1, **_: object) -> pd.DataFrame:
    """Delay case values from effective_year onwards by N years.

    Values pushed beyond the model horizon are dropped. Earlier years are set to
    zero for the affected period until the delayed profile arrives.
    """
    out = df.copy()
    delay_years = int(delay_years)
    affected = out[_case_mask(out, case_id, effective_year)].copy()
    if affected.empty or delay_years <= 0:
        return out

    horizon_max = out["Year"].max()
    out.loc[_case_mask(out, case_id, effective_year), VALUE_COLUMNS] = 0

    shifted = affected.copy()
    shifted["Year"] = shifted["Year"] + delay_years
    shifted = shifted[shifted["Year"] <= horizon_max]

    out = out.merge(
        shifted[["CaseID", "Year", *VALUE_COLUMNS]],
        on=["CaseID", "Year"],
        how="left",
        suffixes=("", "_shifted"),
    )
    for col in VALUE_COLUMNS:
        shifted_col = f"{col}_shifted"
        out[col] = out[shifted_col].combine_first(out[col])
        out = out.drop(columns=[shifted_col])
    return out


def apply_price_adj(df: pd.DataFrame, case_id: str, effective_year: int, price_multiplier: float = 1.0, **_: object) -> pd.DataFrame:
    out = df.copy()
    mask = _case_mask(out, case_id, effective_year)
    out.loc[mask, "Revenue"] = out.loc[mask, "Revenue"] * float(price_multiplier)
    out.loc[mask, "PreTaxCashflow"] = out.loc[mask, "Revenue"] - out.loc[mask, "OPEX"] - out.loc[mask, "CAPEX"]
    return out


def apply_farmdown_proceeds(
    df: pd.DataFrame,
    case_id: str,
    effective_year: int,
    wi_reduction_pct: float = 0.0,
    proceeds: float = 0.0,
    **_: object,
) -> pd.DataFrame:
    """Reduce working interest from effective year and add one-off proceeds."""
    out = df.copy()
    mask = _case_mask(out, case_id, effective_year)
    reduction_factor = 1 - (float(wi_reduction_pct) / 100)
    scale_cols = ["Production", "Revenue", "OPEX", "CAPEX"]
    out.loc[mask, scale_cols] = out.loc[mask, scale_cols] * reduction_factor
    deal_mask = out["CaseID"].eq(case_id) & out["Year"].eq(int(effective_year))
    out.loc[deal_mask, "Revenue"] = out.loc[deal_mask, "Revenue"] + float(proceeds)
    out.loc[mask, "PreTaxCashflow"] = out.loc[mask, "Revenue"] - out.loc[mask, "OPEX"] - out.loc[mask, "CAPEX"]
    return out


def apply_farmdown_carry(
    df: pd.DataFrame,
    case_id: str,
    effective_year: int,
    carry_amount: float = 0.0,
    carry_end_year: int | None = None,
    **_: object,
) -> pd.DataFrame:
    """Apply a CAPEX offset phased evenly until carry is exhausted/end year."""
    out = df.copy()
    carry_end_year = int(carry_end_year or effective_year)
    years = list(range(int(effective_year), carry_end_year + 1))
    if not years:
        return out
    annual_offset = float(carry_amount) / len(years)
    mask = out["CaseID"].eq(case_id) & out["Year"].between(int(effective_year), carry_end_year)
    out.loc[mask, "CAPEX"] = (out.loc[mask, "CAPEX"] - annual_offset).clip(lower=0)
    out.loc[mask, "PreTaxCashflow"] = out.loc[mask, "Revenue"] - out.loc[mask, "OPEX"] - out.loc[mask, "CAPEX"]
    return out


def apply_farmdown_hybrid(df: pd.DataFrame, case_id: str, effective_year: int, **params: object) -> pd.DataFrame:
    out = apply_farmdown_proceeds(df, case_id, effective_year, **params)
    out = apply_farmdown_carry(out, case_id, effective_year, **params)
    return out


OPERATION_FUNCTIONS = {
    "NoChange": lambda df, **kwargs: df.copy(),
    "Exclude": apply_exclude,
    "Delay": apply_delay,
    "PriceAdj": apply_price_adj,
    "FarmDown_Proceeds": apply_farmdown_proceeds,
    "FarmDown_Carry": apply_farmdown_carry,
    "FarmDown_Hybrid": apply_farmdown_hybrid,
}
