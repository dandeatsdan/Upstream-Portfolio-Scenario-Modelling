# ============================================================
# SCENARIO MODELLING ENGINE
# ============================================================
#
# Purpose
# -------
# This module contains the main execution engine for the Upstream
# Portfolio Scenario Modelling application. It coordinates validated
# scenario instructions, case-level modelling operations, financial
# calculations, output construction and final publication of results.
#
# The engine acts as the orchestration layer between the scenario
# configuration prepared in Excel and the reusable transformation
# functions contained within the operations library.
#
# Processing flow
# ---------------
# 1. Read the prepared scenario instructions and identify included cases.
# 2. Route each case to the selected modelling operation using the
#    operation-functions mapping.
# 3. Apply the associated Param1-Param5 inputs to the case profile.
# 4. Consolidate transformed case profiles into scenario-level results.
# 5. Attach scenario, case and organisational metadata.
# 6. Derive tax charge, cash tax, post-tax RCOP and post-tax cash flow.
# 7. Calculate discounted post-tax cash flow for downstream NPV analysis.
# 8. Validate the completed output before publishing it to Excel.
# 9. Generate business and technical execution messages for the model log.
#
# Error handling and publication control
# --------------------------------------
# The engine follows a fail-safe publication pattern. Errors raised by
# individual modelling operations or downstream calculation stages are
# captured together with the relevant scenario, case and operation
# context where available.
#
# A refreshed scenario output is published only when the complete engine
# run remains valid. This prevents partially processed or internally
# inconsistent results from replacing the previous valid model output.
#
# Analytical boundary
# -------------------
# The engine performs deterministic transformations and financial
# calculations from user-defined instructions. It does not select cases,
# determine assumptions, optimise portfolios or recommend a preferred
# scenario. Interpretation and decision-making remain with the user.
#
# Design principles
# -----------------
# Modular execution | Separation of concerns | Explicit validation |
# Traceable processing | Fail-safe publication | Consistent treatment |
# Transparent calculations | Human oversight | Reproducible outputs
#
# ============================================================

# ============================================================
# SCENARIO ENGINE — RUN OPERATIONS
# ============================================================

## This code block defines the range of years for which the model will generate results, ensuring that the output is constrained to a specific timeframe relevant to the analysis.
## It also initializes the run start time, which is used for logging and tracking the execution of the model, providing a timestamp for when the scenario processing began.
## Using the scenario instructions df, the engine iterates through each unique scenario
## processing the included cases and applying the specified operations by calling on the operations functions dictionary to generate the scenario results.

YEAR_MIN, YEAR_MAX = 2026, 2040

run_start = datetime.now()

engine_is_valid = True
engine_error_message = ""
engine_error_scenario = None
engine_error_case_id = None
engine_error_case_name = None
engine_error_operation = None

scenario_results = []
engine_log = []

for scen in scenario_instructions_df["Scenario"].dropna().unique():

    scen_df = scenario_instructions_df.query(
        "Scenario == @scen and Include == True"
    )

    if scen_df.empty:
        engine_log.append({
            "Scenario": scen,
            "IncludedCases": 0,
            "CasesProcessed": 0,
            "OutputRows": 0,
            "Status": "Skipped"
        })
        continue

    scen_results = []
    cases_processed = 0

    for _, r in scen_df.iterrows():

        cid = r["ID"]
        case_name = r["Case Name"]
        op = r["Operation"]

        subset = data_profile_tall.query(
            "ID == @cid"
        ).copy()

        if subset.empty:
            continue

        subset["Scenario"] = scen
        subset["Operation"] = op

        for i in range(1, 6):
            subset[f"Param{i}"] = r[f"Param{i}"]

        try:
            subset = operation_functions[op](
                subset,
                r["Param1"],
                r["Param2"],
                r["Param3"],
                r["Param4"],
                r["Param5"]
            )

        except Exception as exc:
            engine_is_valid = False
            engine_error_message = str(exc)
            engine_error_scenario = scen
            engine_error_case_id = cid
            engine_error_case_name = case_name
            engine_error_operation = op
            break

        subset = subset.loc[
            subset["Year"].between(
                YEAR_MIN,
                YEAR_MAX
            )
        ].copy()

        scen_results.append(subset)
        cases_processed += 1

    if not engine_is_valid:
        break

    if not scen_results:
        engine_log.append({
            "Scenario": scen,
            "IncludedCases": len(scen_df),
            "CasesProcessed": 0,
            "OutputRows": 0,
            "Status": "No output"
        })
        continue

    scen_combined = pd.concat(
        scen_results,
        ignore_index=True
    )

    scenario_results.append(scen_combined)

    engine_log.append({
        "Scenario": scen,
        "IncludedCases": len(scen_df),
        "CasesProcessed": cases_processed,
        "OutputRows": len(scen_combined),
        "Status": "Completed"
    })

if not scenario_results and not engine_error_message:
    engine_is_valid = False
    engine_error_message = (
        "No scenario results were generated."
    )

## This boolean flag indicates whether the engine executed successfully without errors.
## It is used to control the flow of the application and determine whether to proceed with further processing or handle errors accordingly.

engine_is_valid

# ============================================================
# SCENARIO ENGINE — BUILD PRE-TAX OUTPUT
# ============================================================

## This code block consolidates the results from all processed scenarios into a single dataframe, adding metadata such as the run date and time, scenario names, and case attributes. It ensures that the output is structured and ready for further analysis or reporting. If any errors occur during this process, the engine's validity flag is set to False, and relevant error information is captured for debugging and user feedback.

if engine_is_valid:

    try:
        scenario_outputs_pre_tax = pd.concat(
            scenario_results,
            ignore_index=True
        )

        scenario_outputs_pre_tax["RunDateTime"] = (
            run_start.strftime("%Y-%m-%d %H:%M:%S")
        )

        scenario_outputs_pre_tax = (
            scenario_outputs_pre_tax.merge(
                scenario_meta.rename(
                    columns={"Name": "Scenario Name"}
                ),
                on="Scenario",
                how="left",
                validate="many_to_one"
            )
        )

        case_attributes = case_listing[
            [
                "ID",
                "Group Entity",
                "Segment",
                "Region",
                "Country",
                "Country Key",
                "Plan Type",
                "Case Name"
            ]
        ].copy()

        scenario_outputs_pre_tax = (
            scenario_outputs_pre_tax.merge(
                case_attributes,
                on="ID",
                how="left",
                validate="many_to_one"
            )
        )

    except Exception as exc:
        engine_is_valid = False
        engine_error_message = str(exc)
        engine_error_operation = (
            "Build pre-tax output"
        )

engine_is_valid

# ============================================================
# SCENARIO ENGINE — POST-TAX CALCULATIONS
# ============================================================

## This code block performs post-tax calculations on the pre-tax scenario outputs, applying tax rates to compute metrics such as tax charges, cash tax payments, post-tax RCOP, and post-tax cash flow.
## It merges the necessary tax rate data, handles any missing values, and generates additional rows in the output dataframe to reflect the calculated post-tax metrics.
## If any errors occur during this process, the engine's validity flag is set to False, and relevant error information is captured for debugging and user feedback.
## The results of the post-tax calculations are essential for understanding the financial implications of each scenario, providing users with a comprehensive view of the outcomes after accounting for tax effects.

URCOP_METRIC = "Underlying RCOP"
PRE_TAX_FCF_METRIC = "Pre Tax Cash Flow"

TAX_CHARGE_METRIC = "Tax Charge"
CASH_TAX_METRIC = "Cash Tax Payment"
POST_TAX_RCOP_METRIC = "Post-Tax RCOP"
POST_TAX_FCF_METRIC = "Post-Tax Cash Flow"

if engine_is_valid:

    try:
        scenario_outputs = (
            scenario_outputs_pre_tax.copy()
        )

        scenario_outputs["Country Key"] = (
            scenario_outputs["Country Key"]
            .astype("string")
            .str.strip()
        )

        scenario_outputs["_TaxYear"] = (
            scenario_outputs["Year"]
            .astype("Int64")
            .astype("string")
        )

        tax_merge = tax_rates[
            [
                "Country Key",
                "Year",
                "ETR",
                "CTR"
            ]
        ].copy()

        tax_merge["Country Key"] = (
            tax_merge["Country Key"]
            .astype("string")
            .str.strip()
        )

        tax_merge["_TaxYear"] = (
            tax_merge["Year"]
            .astype("string")
            .str.strip()
        )

        tax_merge = tax_merge.drop(
            columns="Year"
        )

        scenario_outputs = scenario_outputs.merge(
            tax_merge,
            on=[
                "Country Key",
                "_TaxYear"
            ],
            how="left",
            validate="many_to_one"
        )

        urcop = scenario_outputs.loc[
            scenario_outputs["Metric"]
            == URCOP_METRIC
        ].copy()

        fcf = scenario_outputs.loc[
            scenario_outputs["Metric"]
            == PRE_TAX_FCF_METRIC
        ].copy()

        if urcop.empty:
            raise ValueError(
                f"Metric '{URCOP_METRIC}' was not found."
            )

        if fcf.empty:
            raise ValueError(
                f"Metric '{PRE_TAX_FCF_METRIC}' was not found."
            )

        missing_rates = (
            urcop["ETR"].isna()
            | urcop["CTR"].isna()
        )

        if missing_rates.any():
            missing_count = (
                urcop.loc[
                    missing_rates,
                    ["Country Key", "Year"]
                ]
                .drop_duplicates()
                .shape[0]
            )

            raise ValueError(
                f"Missing tax rates for "
                f"{missing_count:,} country-year combinations."
            )

        urcop["_TaxableURCOP"] = (
            urcop["Value"].clip(lower=0)
        )

        urcop["_TaxCharge"] = (
            urcop["_TaxableURCOP"]
            * urcop["ETR"]
        )

        urcop["_CashTax"] = (
            urcop["_TaxableURCOP"]
            * urcop["CTR"]
        )

        tax_charge = urcop.copy()
        tax_charge["Metric"] = TAX_CHARGE_METRIC
        tax_charge["Value"] = -tax_charge["_TaxCharge"]

        cash_tax = urcop.copy()
        cash_tax["Metric"] = CASH_TAX_METRIC
        cash_tax["Value"] = -cash_tax["_CashTax"]

        post_tax_rcop = urcop.copy()
        post_tax_rcop["Metric"] = POST_TAX_RCOP_METRIC
        post_tax_rcop["Value"] = (
            post_tax_rcop["Value"]
            - post_tax_rcop["_TaxCharge"]
        )

        cash_tax_lookup = urcop[
            [
                "Scenario",
                "ID",
                "Year",
                "_CashTax"
            ]
        ].copy()

        fcf = fcf.merge(
            cash_tax_lookup,
            on=[
                "Scenario",
                "ID",
                "Year"
            ],
            how="left",
            validate="one_to_one"
        )

        missing_cash_tax_matches = (
            fcf.loc[
                fcf["_CashTax"].isna(),
                [
                    "Scenario",
                    "ID",
                    "Case Name",
                    "Country",
                    "Year",
                    "Value",
                    "_CashTax"
                ]
            ]
            .copy()
        )

        # Where no corresponding cash tax value exists,
        # treat cash tax as zero.
        fcf["_CashTax"] = (
            fcf["_CashTax"]
            .fillna(0)
        )

        post_tax_fcf = fcf.copy()
        post_tax_fcf["Metric"] = POST_TAX_FCF_METRIC
        post_tax_fcf["Value"] = (
            post_tax_fcf["Value"]
            - post_tax_fcf["_CashTax"]
        )

        output_columns = (
            scenario_outputs.columns.tolist()
        )

        calculated_rows = [
            tax_charge[output_columns],
            cash_tax[output_columns],
            post_tax_rcop[output_columns],
            post_tax_fcf[output_columns]
        ]

        scenario_outputs = pd.concat(
            [
                scenario_outputs,
                *calculated_rows
            ],
            ignore_index=True
        )

        scenario_outputs = scenario_outputs.drop(
            columns=[
                "_TaxYear",
                "ETR",
                "CTR"
            ],
            errors="ignore"
        )

        output_columns_final = [
            "Scenario",
            "Scenario Name",
            "Scenario Description",
            "ID",
            "Case",
            "Case Name",
            "Group Entity",
            "Segment",
            "Region",
            "Country",
            "Country Key",
            "Plan Type",
            "Operation",
            "Param1",
            "Param2",
            "Param3",
            "Param4",
            "Param5",
            "Metric",
            "Year",
            "Value",
            "RunDateTime"
        ]

        candidate_scenario_outputs_tall = (
            scenario_outputs[
                output_columns_final
            ].copy()
        )

    except Exception as exc:
        engine_is_valid = False
        engine_error_message = str(exc)
        engine_error_operation = (
            "Post-tax calculations"
        )

engine_is_valid

# ============================================================
# SCENARIO ENGINE — DISCOUNTED POST-TAX CASH FLOW
# ============================================================

## This code block calculates the discounted post-tax cash flow for each scenario, applying a specified discount rate to the post-tax cash flow metric.
## It generates additional rows in the output dataframe to reflect the discounted values, which are essential for financial analysis and decision-making.
## If any errors occur during this process, the engine's validity flag is set to False, and relevant error information is captured for debugging and user feedback.
## The discounted post-tax cash flow provides a present value perspective on the future cash flows, allowing users to assess the financial viability of different scenarios and make informed investment decisions.
## Net Present Value (NPV) is calculated in Power Pivot using a DAX measure to sum up the discounted post-tax cash flow values for each case or any aggregtino of case, providing a single metric that reflects the overall financial performance of the scenario after accounting for the time value of money.

NPV_RATE = 0.08
NPV_BASE_YEAR = 2026
NPV_SOURCE_METRIC = "Post-Tax Cash Flow"
DISCOUNTED_CF_METRIC = "Discounted Post-Tax Cash Flow @ 8%"

if engine_is_valid:

    try:

        discounted_cf = (
            candidate_scenario_outputs_tall.loc[
                candidate_scenario_outputs_tall["Metric"]
                == NPV_SOURCE_METRIC
            ]
            .copy()
        )

        if discounted_cf.empty:
            raise ValueError(
                f"NPV source metric "
                f"'{NPV_SOURCE_METRIC}' was not found."
            )

        # Excel NPV convention:
        # 2026 = Period 1
        # 2027 = Period 2
        # ...
        # 2040 = Period 15
        discounted_cf["DiscountPeriod"] = (
            discounted_cf["Year"]
            - NPV_BASE_YEAR
            + 1
        )

        discounted_cf["Value"] = (
            discounted_cf["Value"]
            / (
                (1 + NPV_RATE)
                ** discounted_cf["DiscountPeriod"]
            )
        )

        discounted_cf["Metric"] = (
            DISCOUNTED_CF_METRIC
        )

        discounted_cf = discounted_cf.drop(
            columns=["DiscountPeriod"],
            errors="ignore"
        )

        candidate_scenario_outputs_tall = pd.concat(
            [
                candidate_scenario_outputs_tall,
                discounted_cf[
                    candidate_scenario_outputs_tall.columns
                ]
            ],
            ignore_index=True
        )

    except Exception as exc:

        engine_is_valid = False
        engine_error_message = str(exc)
        engine_error_operation = (
            "Discounted post-tax cash flow calculation"
        )

engine_is_valid

# ============================================================
# SCENARIO ENGINE — VALIDATE AND PUBLISH
# ============================================================

## This code block validates the final scenario outputs, ensuring that the results are complete and accurate before publishing them for further analysis or reporting.
## It generates a summary of the validation results, including the number of scenarios completed, cases processed, output rows generated, and any missing hierarchy cases.
## The results are output into an Excel spilled array and then captured by Power Pivot for further analysis, allowing users to explore the results and derive insights from the scenario outputs.
## The users are provided with a light-weight dashboard functionality in Excel via Power Pivot (Excel data model) to explore the results and derive insights from the scenario outputs, enabling them to make informed decisions based on the analysis of different scenarios.

engine_validation_summary = pd.DataFrame(
    engine_log
)

if engine_is_valid:

    missing_hierarchy_cases = (
        candidate_scenario_outputs_tall.loc[
            candidate_scenario_outputs_tall[
                [
                    "Group Entity",
                    "Segment",
                    "Region",
                    "Country",
                    "Country Key",
                    "Plan Type"
                ]
            ].isna().any(axis=1),
            "ID"
        ]
        .nunique()
    )

    engine_validation_totals = {
        "ScenariosCompleted": int(
            (
                engine_validation_summary["Status"]
                == "Completed"
            ).sum()
        ),
        "ScenariosSkipped": int(
            (
                engine_validation_summary["Status"]
                != "Completed"
            ).sum()
        ),
        "CasesProcessed": int(
            engine_validation_summary[
                "CasesProcessed"
            ].sum()
        ),
        "OutputRows": len(
            candidate_scenario_outputs_tall
        ),
        "UniqueCases": int(
            candidate_scenario_outputs_tall[
                "ID"
            ].nunique()
        ),
        "MissingHierarchyCases": int(
            missing_hierarchy_cases
        ),
        "RunSeconds": (
            datetime.now() - run_start
        ).total_seconds()
    }

    scenario_outputs_tall = (
        candidate_scenario_outputs_tall
    )

else:

    if not engine_error_message:
        engine_error_message = (
            "The scenario engine did not generate "
            "a valid output."
        )

    engine_validation_totals = {
        "ScenariosCompleted": int(
            sum(
                row["Status"] == "Completed"
                for row in engine_log
            )
        ),
        "ScenariosSkipped": int(
            sum(
                row["Status"] != "Completed"
                for row in engine_log
            )
        ),
        "CasesProcessed": int(
            sum(
                row["CasesProcessed"]
                for row in engine_log
            )
        ),
        "OutputRows": 0,
        "UniqueCases": 0,
        "MissingHierarchyCases": 0,
        "RunSeconds": (
            datetime.now() - run_start
        ).total_seconds()
    }

engine_is_valid

# ============================================================
# ENGINE VALIDATION MESSAGES
# ============================================================

## This final code block generates validation messages for the scenario engine, providing a summary of the execution results, including the number of scenarios completed, cases processed, output rows generated, and any missing hierarchy cases.
## The results are returned to the user via the model log on the application home page, providing both business and technical details for users to understand the validation outcomes.

if engine_is_valid:

    engine_validation_status = (
        "✅ Scenario engine completed successfully."
    )

    engine_validation_business_message = (
        f"The modelling engine processed "
        f"{engine_validation_totals['CasesProcessed']:,} case operations "
        f"and generated updated scenario results."
    )

    engine_validation_technical_detail = (
        f"🟩 {engine_validation_totals['ScenariosCompleted']:,} "
        f"scenarios completed; "
        f"{engine_validation_totals['ScenariosSkipped']:,} skipped.\n"
        f"🟦 {engine_validation_totals['CasesProcessed']:,} "
        f"case operations processed.\n"
        f"🟪 {engine_validation_totals['OutputRows']:,} rows generated "
        f"across {engine_validation_totals['UniqueCases']:,} cases.\n"
        f"🟨 {engine_validation_totals['MissingHierarchyCases']:,} "
        f"cases have incomplete hierarchy attributes.\n"
        f"⏱️ Completed in "
        f"{engine_validation_totals['RunSeconds']:.2f} seconds."
    )

else:

    engine_validation_status = (
        "❌ Scenario engine run failed."
    )

    if engine_error_case_id is not None:

        engine_validation_business_message = (
            f"Scenario {engine_error_scenario} could not process "
            f"'{engine_error_case_name}' "
            f"(ID {engine_error_case_id}) using operation "
            f"'{engine_error_operation}'. "
            f"Review the scenario configuration and run the engine again."
        )

        engine_validation_technical_detail = (
            f"🟥 Scenario: {engine_error_scenario}\n"
            f"🟥 Case: {engine_error_case_name} "
            f"(ID {engine_error_case_id})\n"
            f"🟧 Operation: {engine_error_operation}\n"
            f"⬛ Error: {engine_error_message}\n"
            f"⚠️ No refreshed scenario output was produced."
        )

    else:

        engine_validation_business_message = (
            "The scenario engine did not generate a valid result dataset. "
            "Review the scenario configuration and input data before "
            "running the engine again."
        )

        engine_validation_technical_detail = (
            f"🟥 Error: {engine_error_message}\n"
            f"🟦 {engine_validation_totals['CasesProcessed']:,} "
            f"case operations were processed before the run stopped.\n"
            f"⏱️ Run stopped after "
            f"{engine_validation_totals['RunSeconds']:.2f} seconds.\n"
            f"⚠️ No refreshed scenario output was produced."
        )

engine_validation_status