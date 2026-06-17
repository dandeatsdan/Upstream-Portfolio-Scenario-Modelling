from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from engine.scenario_engine import compare_to_baseline, npv, run_scenario

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"

st.set_page_config(page_title="Scenario Modeller MVP", layout="wide")


@st.cache_data
def load_cases() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "baseline_cases.csv")


@st.cache_data
def load_financials() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "baseline_financials.csv")


def to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()


cases = load_cases()
baseline = load_financials()

st.title("Scenario Modeller MVP")
st.caption("Prototype interface for configuring portfolio scenario operations and running a Python calculation engine.")

with st.sidebar:
    st.header("Scenario setup")
    scenario_name = st.text_input("Scenario name", value="Downside Delay Case")
    baseline_version = st.selectbox("Baseline version", ["April 2026 Group Feed", "Mock Baseline v1"])
    description = st.text_area("Description", value="Test selected portfolio changes against the baseline.")
    discount_rate = st.number_input("Discount rate", min_value=0.0, max_value=0.5, value=0.10, step=0.01)

st.subheader("1. Select cases and operations")

editable_cases = cases.copy()
editable_cases["Include"] = True
editable_cases["Operation"] = "NoChange"
editable_cases["EffectiveYear"] = 2026
editable_cases["DelayYears"] = 0
editable_cases["PriceMultiplier"] = 1.00
editable_cases["WIReductionPct"] = 0.0
editable_cases["Proceeds"] = 0.0
editable_cases["CarryAmount"] = 0.0
editable_cases["CarryEndYear"] = 2026

configured = st.data_editor(
    editable_cases,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Include": st.column_config.CheckboxColumn("Include"),
        "Operation": st.column_config.SelectboxColumn(
            "Operation",
            options=[
                "NoChange",
                "Exclude",
                "Delay",
                "PriceAdj",
                "FarmDown_Proceeds",
                "FarmDown_Carry",
                "FarmDown_Hybrid",
            ],
        ),
        "EffectiveYear": st.column_config.NumberColumn("Effective year", min_value=2026, max_value=2040, step=1),
        "DelayYears": st.column_config.NumberColumn("Delay years", min_value=0, max_value=10, step=1),
        "PriceMultiplier": st.column_config.NumberColumn("Price multiplier", min_value=0.0, max_value=3.0, step=0.05, format="%.2f"),
        "WIReductionPct": st.column_config.NumberColumn("WI reduction %", min_value=0.0, max_value=100.0, step=5.0),
        "Proceeds": st.column_config.NumberColumn("Proceeds", min_value=0.0, step=10.0),
        "CarryAmount": st.column_config.NumberColumn("Carry amount", min_value=0.0, step=10.0),
        "CarryEndYear": st.column_config.NumberColumn("Carry end year", min_value=2026, max_value=2040, step=1),
    },
)

st.subheader("2. Operation table")
operation_table = configured.rename(
    columns={
        "EffectiveYear": "effective_year",
        "DelayYears": "delay_years",
        "PriceMultiplier": "price_multiplier",
        "WIReductionPct": "wi_reduction_pct",
        "Proceeds": "proceeds",
        "CarryAmount": "carry_amount",
        "CarryEndYear": "carry_end_year",
    }
)
operation_table = operation_table[operation_table["Include"].eq(True)].copy()
operation_table = operation_table[operation_table["Operation"].ne("NoChange")].copy()
operation_table = operation_table[
    [
        "CaseID",
        "Operation",
        "effective_year",
        "delay_years",
        "price_multiplier",
        "wi_reduction_pct",
        "proceeds",
        "carry_amount",
        "carry_end_year",
    ]
]
operation_table = operation_table.rename(columns={"CaseID": "case_id"})

excluded = configured[configured["Include"].eq(False)].copy()
if not excluded.empty:
    extra_exclusions = excluded[["CaseID"]].rename(columns={"CaseID": "case_id"})
    extra_exclusions["Operation"] = "Exclude"
    extra_exclusions["effective_year"] = 2026
    extra_exclusions["delay_years"] = 0
    extra_exclusions["price_multiplier"] = 1.0
    extra_exclusions["wi_reduction_pct"] = 0.0
    extra_exclusions["proceeds"] = 0.0
    extra_exclusions["carry_amount"] = 0.0
    extra_exclusions["carry_end_year"] = 2026
    operation_table = pd.concat([operation_table, extra_exclusions], ignore_index=True)

st.dataframe(operation_table, use_container_width=True, hide_index=True)

run = st.button("Run scenario", type="primary")

if run:
    scenario = run_scenario(baseline, operation_table)
    comparison = compare_to_baseline(baseline, scenario)

    baseline_npv = npv(baseline, discount_rate)
    scenario_npv = npv(scenario, discount_rate)
    delta_npv = scenario_npv - baseline_npv

    st.subheader("3. Results summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline NPV", f"{baseline_npv:,.0f}")
    c2.metric("Scenario NPV", f"{scenario_npv:,.0f}")
    c3.metric("NPV movement", f"{delta_npv:,.0f}")

    chart_metric = st.selectbox(
        "Chart metric",
        ["Production", "Revenue", "OPEX", "CAPEX", "PreTaxCashflow"],
        index=4,
    )
    chart_df = comparison[["Year", f"{chart_metric}_Baseline", f"{chart_metric}_Scenario"]].melt(
        id_vars="Year", var_name="Series", value_name="Value"
    )
    fig = px.line(chart_df, x="Year", y="Value", color="Series", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("4. Baseline vs scenario comparison")
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    export_bytes = to_excel_bytes(
        {
            "Scenario_Setup": pd.DataFrame(
                [
                    {
                        "ScenarioName": scenario_name,
                        "BaselineVersion": baseline_version,
                        "Description": description,
                        "DiscountRate": discount_rate,
                    }
                ]
            ),
            "Operation_Table": operation_table,
            "Baseline": baseline,
            "Scenario": scenario,
            "Comparison": comparison,
        }
    )
    st.download_button(
        "Download scenario workbook",
        data=export_bytes,
        file_name=f"{scenario_name.replace(' ', '_')}_scenario_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Configure the scenario, then select **Run scenario**.")
