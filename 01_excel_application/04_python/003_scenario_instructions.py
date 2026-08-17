# ============================================================
# SCENARIO XL ARRAY DEFINITION
# ============================================================

## This code block defines the Excel array references for each scenario configuration, allowing for the retrieval of scenario instructions from the corresponding Excel tables. Each scenario is associated with a specific table in the Excel workbook, and the xl() function is used to access the data within those tables, including headers. The resulting dataframes are stored in a dictionary for further processing and validation.
## It captures the scenario instructions from the Excel tables and prepares them for validation and execution within the application.
## It replaces operation names the user inputs via a data validation drop-down in Excel with the corresponding engine keys, ensuring that the instructions are correctly interpreted by the application.

scenario_sources = {
    "S1": xl("Scenario_S1[#All]", headers=True),
    "S2": xl("Scenario_S2[#All]", headers=True),
    "S3": xl("Scenario_S3[#All]", headers=True),
    "S4": xl("Scenario_S4[#All]", headers=True),
    "S5": xl("Scenario_S5[#All]", headers=True),
}

# ============================================================
# OPERATION MAPPINGS
# ============================================================

OPERATION_MAP = {
    "No Change": "NoChange",
    "Delay": "Delay",
    "Accelerate": "Accelerate",
    "Farm In (Increase)": "Increase",
    "Farm Down (Dilution)": "Dilution",
    "Truncate Before": "TruncateBefore",
    "Truncate After": "TruncateAfter",
    "Production Change %": "ProdnAdj",
    "OPEX Change %": "CostAdjOpex",
    "CAPEX Change %": "CostAdjCapex",
    "CAPEX Change $m": "CapexAbsolute",
    "OPEX Change $m": "OpexAbsolute",
}

# ============================================================
# SCENARIO PREPARATION
# ============================================================

validation_log = []


def prepare_scenario_table(df, scenario_id):

    out = df.copy()

    # Rename columns
    out = out.rename(
        columns={
            "Case ID": "ID",
            "Included (y/n)": "Include",
            "Choose Operation": "Operation",
            "Input 1": "Param1",
            "Input 2": "Param2",
            "Input 3": "Param3",
            "Input 4": "Param4",
            "Input 5": "Param5"
        }
    )

    # Keep only required columns
    out = out[
        [
            "ID",
            "Case Name",
            "Include",
            "Operation",
            "Param1",
            "Param2",
            "Param3",
            "Param4",
            "Param5"
        ]
    ].copy()

    # Add scenario identifier
    out["Scenario"] = scenario_id

    # Remove completely blank rows
    out = out.dropna(
        subset=["ID", "Case Name"],
        how="all"
    ).copy()

    # Remove placeholder rows
    out = out[
        out["Case Name"].notna()
        & out["Case Name"].str.casefold().ne("no case")
    ].copy()

    # Clean ID
    out["ID"] = pd.to_numeric(
        out["ID"],
        errors="coerce"
    ).astype("Int64")

    # Convert inclusion flag to Boolean
    out["Include"] = (
        out["Include"]
        .astype("string")
        .str.strip()
        .map(
            {
                "Yes": True,
                "No": False
            }
        )
        .fillna(False)
        .astype(bool)
    )

    # Map user-facing operation labels to engine keys
    out["Operation"] = out["Operation"].map(
        OPERATION_MAP
    ).astype(object)

    # Count excluded rows that still contain a mapped operation
    excluded_operations = (
        (~out["Include"])
        & out["Operation"].notna()
    ).sum()

    # Clear operation for excluded cases
    out.loc[
        ~out["Include"],
        "Operation"
    ] = None

    # Count included rows with a blank or invalid operation
    defaulted_operations = (
        out["Include"]
        & out["Operation"].isna()
    ).sum()

    # Included cases with a blank or invalid operation default to NoChange
    out.loc[
        out["Include"]
        & out["Operation"].isna(),
        "Operation"
    ] = "NoChange"

    # Clean numeric parameters
    param_cols = [
        "Param1",
        "Param2",
        "Param3",
        "Param4",
        "Param5"
    ]

    for col in param_cols:
        out[col] = pd.to_numeric(
            out[col],
            errors="coerce"
        ).fillna(0)

    # Count rows containing stale parameters that will be reset
    stale_parameters = (
        (
            (~out["Include"])
            | (out["Operation"] == "NoChange")
        )
        & out[param_cols].ne(0).any(axis=1)
    ).sum()

    # Clear parameters for excluded cases or NoChange operations
    out.loc[
        (~out["Include"])
        | (out["Operation"] == "NoChange"),
        param_cols
    ] = 0

    # Record aggregated validation actions for this scenario
    validation_log.append(
        {
            "Scenario": scenario_id,
            "RowsProcessed": len(out),
            "ExcludedOperationsCleared": excluded_operations,
            "OperationsDefaultedToNoChange": defaulted_operations,
            "ParameterSetsCleared": stale_parameters,
        }
    )

    # Final column order
    return out[
        [
            "Scenario",
            "ID",
            "Case Name",
            "Include",
            "Operation",
            "Param1",
            "Param2",
            "Param3",
            "Param4",
            "Param5"
        ]
    ].reset_index(drop=True)

# ============================================================
# SCENARIO CLEAN, PREPARE AND CONSOLIDATE
# ============================================================

scenario_instructions_df = pd.concat(
    [
        prepare_scenario_table(df, scenario)
        for scenario, df in scenario_sources.items()
    ],
    ignore_index=True
)

validation_summary = pd.DataFrame(validation_log)

# ============================================================
# SCENARIO METADATA
# ============================================================

## This code block retrieves the scenario metadata from the Excel table "scen_meta" and stores it in a dataframe for further processing. The metadata includes information about each scenario configuration, such as scenario identifiers, descriptions, and any other relevant attributes. This metadata is essential for understanding the context of the scenario instructions and for ensuring that the scenarios are executed correctly within the application.
## It contains scenario ID, name, description, and other relevant attributes, which are essential for understanding the context of the scenario instructions and for ensuring that the scenarios are executed correctly within the application.

scenario_meta =  xl("scen_meta[#All]", headers=True)


# ============================================================
# SCENARIO VALIDATION MESSAGES
# ============================================================

## This code block generates validation messages for the scenario instructions dataframe, providing a summary of the validation results, including the number of instruction rows processed, operations cleared for excluded cases, operations defaulted to NoChange, stale parameter sets reset, and the total number of scenario configurations prepared. The results are returned to the user via the model log on the application home page, providing both business and technical details for users to understand the validation outcomes.
## The results are returned to the user via the model log on the application home page, providing both business and technical details for users to understand the validation outcomes.

scenario_validation_status = (
    "✅ Scenario instructions prepared successfully."
)

scenario_validation_business_message = (
    "Scenario instructions have been validated and prepared for execution "
    "across all configured scenarios."
)

scenario_validation_technical_detail = (
    f"🟩 {validation_summary['RowsProcessed'].sum():,} instruction rows processed.\n"
    f"🟦 {validation_summary['ExcludedOperationsCleared'].sum():,} operations on excluded cases cleared.\n"
    f"🟪 {validation_summary['OperationsDefaultedToNoChange'].sum():,} blank or invalid operations defaulted to NoChange.\n"
    f"⬛ {validation_summary['ParameterSetsCleared'].sum():,} stale parameter sets reset.\n"
    f"📊 {len(validation_summary):,} scenario configurations prepared."
)

scenario_validation_status