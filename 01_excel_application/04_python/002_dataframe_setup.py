####################################
## DATAFRAME SETUP + VALIDATION ####
####################################

# ============================================================
# CASE LISTING DATAFRAME
# ============================================================

## This code blocks sets up the CaseListing dataframe by importing data from Excel, cleaning the column structure and field values, removing invalid records, validating unique IDs and case names, checking hierarchy completeness, and finalizing the dataframe for further processing.

case_listing = xl(
    "CaseListing[#All]",
    headers=True
).copy()

rows_imported = len(case_listing)


# ============================================================
# CLEAN COLUMN STRUCTURE
# ============================================================

case_listing.columns = (
    case_listing.columns
    .astype(str)
    .str.strip()
    .str.removeprefix("[")
    .str.removesuffix("]")
)

case_listing = case_listing.rename(
    columns={"Index": "ID"}
)

required_columns = [
    "ID",
    "Case",
    "Group Entity",
    "Segment",
    "Region",
    "Country",
    "Plan Type",
    "Case Name",
    "Country Key"
]

missing_columns = [
    column
    for column in required_columns
    if column not in case_listing.columns
]

if missing_columns:
    raise ValueError(
        "CaseListing is missing required columns: "
        + ", ".join(missing_columns)
    )

case_listing = case_listing[
    required_columns
].copy()


# ============================================================
# CLEAN FIELD VALUES
# ============================================================

text_columns = [
    "Case",
    "Group Entity",
    "Segment",
    "Region",
    "Country",
    "Plan Type",
    "Case Name",
    "Country Key"
]

for col in text_columns:
    case_listing[col] = (
        case_listing[col]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

case_listing["ID"] = pd.to_numeric(
    case_listing["ID"],
    errors="coerce"
)


# ============================================================
# REMOVE INVALID RECORDS
# ============================================================

invalid_record_mask = case_listing[
    [
        "ID",
        "Case",
    ]
].isna().any(axis=1)

invalid_records_removed = int(
    invalid_record_mask.sum()
)

case_listing = case_listing.loc[
    ~invalid_record_mask
].copy()

case_listing["ID"] = (
    case_listing["ID"]
    .astype(int)
)

rows_retained = len(case_listing)


# ============================================================
# VALIDATE UNIQUE IDS AND CASE NAMES
# ============================================================

duplicate_id_mask = case_listing.duplicated(
    subset=["ID"],
    keep=False
)

duplicate_case_mask = case_listing.duplicated(
    subset=["Case"],
    keep=False
)

duplicate_id_count = int(
    case_listing.loc[
        duplicate_id_mask,
        "ID"
    ].nunique()
)

duplicate_case_count = int(
    case_listing.loc[
        duplicate_case_mask,
        "Case"
    ].nunique()
)

duplicate_record_mask = (
    duplicate_id_mask
    | duplicate_case_mask
)

case_listing_duplicate_records = (
    case_listing.loc[
        duplicate_record_mask
    ]
    .sort_values(
        [
            "Case",
            "ID"
        ]
    )
    .reset_index(drop=True)
)

case_listing_is_valid = (
    duplicate_id_count == 0
    and duplicate_case_count == 0
)


# ============================================================
# CHECK HIERARCHY COMPLETENESS
# ============================================================

hierarchy_columns = [
    "Group Entity",
    "Segment",
    "Region",
    "Country",
    "Plan Type",
    "Country Key"
]

incomplete_hierarchy_rows = int(
    case_listing[
        hierarchy_columns
    ].isna().any(axis=1).sum()
)


# ============================================================
# FINALISE DATAFRAME
# ============================================================

case_listing_validation_summary = {
    "RowsImported": rows_imported,
    "RowsRetained": rows_retained,
    "InvalidRecordsRemoved": invalid_records_removed,
    "IncompleteHierarchyRows": incomplete_hierarchy_rows,
    "UniqueCaseIDs": case_listing["ID"].nunique(),
    "UniqueCaseNames": case_listing["Case"].nunique(),
    "DuplicateIDs": duplicate_id_count,
    "DuplicateCaseNames": duplicate_case_count,
    "DuplicateRows": len(case_listing_duplicate_records),
    "IsValid": case_listing_is_valid,
}

case_listing = (
    case_listing
    .sort_values(
        by=[
            "Group Entity",
            "Segment",
            "Region",
            "Country",
            "Country Key",
            "Plan Type",
            "Case",
            "Case Name",
            "ID",
        ],
        ascending=True,
        na_position="last",
    )
    .reset_index(drop=True)
)

# ============================================================
# CASE LISTING VALIDATION OUTPUTS
# ============================================================

## This code block generates validation messages for the CaseListing dataframe, providing a summary of the validation results, 
## including the number of valid rows retained, invalid records removed, incomplete hierarchy rows, and any duplicate IDs or case names found.
## The messages are structured to provide both business and technical details for users to understand the validation outcomes.
## In the Excel application these messages are displayed to the user via the model log on the application home page.

if case_listing_is_valid:

    case_listing_status = (
        "✅ Case listing loaded and validated successfully."
    )

    case_listing_business_message = (
        "Portfolio case definitions are ready for scenario modelling."
    )

    case_listing_technical_detail = (
        f"🟩 {case_listing_validation_summary['RowsRetained']:,} valid rows retained "
        f"from {case_listing_validation_summary['RowsImported']:,} imported.\n"
        f"🟦 {case_listing_validation_summary['InvalidRecordsRemoved']:,} invalid records removed.\n"
        f"🟪 {case_listing_validation_summary['IncompleteHierarchyRows']:,} rows contain incomplete hierarchy attributes.\n"
        f"⬛ {case_listing_validation_summary['UniqueCaseIDs']:,} unique case IDs and "
        f"{case_listing_validation_summary['UniqueCaseNames']:,} unique case names validated."
    )

else:

    case_listing_status = (
        "❌ Case listing validation failed."
    )

    case_listing_business_message = (
        "The scenario engine cannot run until duplicate case records are resolved."
    )

    case_listing_technical_detail = (
        f"🟥 {case_listing_validation_summary['DuplicateCaseNames']:,} duplicate case names found.\n"
        f"🟥 {case_listing_validation_summary['DuplicateIDs']:,} duplicate case IDs found.\n"
        f"🟧 {case_listing_validation_summary['DuplicateRows']:,} affected rows identified.\n"
        f"⬛ Review the duplicate-record output and correct the CaseListing table."
    )

case_listing_status

# ============================================================
# TAX RATES DATAFRAME
# ============================================================

## This code block sets up the TaxRates dataframe by importing data from Excel, cleaning the column structure and field values, validating records for completeness and valid rate ranges, checking for duplicate records, and finalizing the dataframe for further processing.

tax_rates = xl(
    "TaxRates[#All]",
    headers=True
).copy()

rows_imported = len(tax_rates)


# ============================================================
# CLEAN COLUMN STRUCTURE
# ============================================================

tax_rates.columns = (
    tax_rates.columns
    .astype(str)
    .str.strip()
    .str.removeprefix("[")
    .str.removesuffix("]")
)

required_columns = [
    "Country",
    "Country Key",
    "Year",
    "ETR",
    "CTR",
]

missing_columns = [
    column
    for column in required_columns
    if column not in tax_rates.columns
]

if missing_columns:
    raise ValueError(
        "TaxRates is missing required columns: "
        + ", ".join(missing_columns)
    )

tax_rates = tax_rates[
    required_columns
].copy()


# ============================================================
# CLEAN FIELD VALUES
# ============================================================

text_columns = [
    "Country",
    "Country Key",
    "Year",
]

for col in text_columns:
    tax_rates[col] = (
        tax_rates[col]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

tax_rates["ETR"] = pd.to_numeric(
    tax_rates["ETR"],
    errors="coerce",
)

tax_rates["CTR"] = pd.to_numeric(
    tax_rates["CTR"],
    errors="coerce",
)


# ============================================================
# VALIDATE RECORDS
# ============================================================

invalid_record_mask = tax_rates[
    [
        "Country Key",
        "Year",
        "ETR",
        "CTR",
    ]
].isna().any(axis=1)

invalid_record_count = int(
    invalid_record_mask.sum()
)

invalid_rate_mask = (
    ~tax_rates["ETR"].between(0, 1)
    | ~tax_rates["CTR"].between(0, 1)
)

invalid_rate_count = int(
    invalid_rate_mask.sum()
)

duplicate_record_mask = tax_rates.duplicated(
    subset=[
        "Country Key",
        "Year",
    ],
    keep=False,
)

duplicate_record_count = int(
    duplicate_record_mask.sum()
)

tax_rates_is_valid = (
    invalid_record_count == 0
    and invalid_rate_count == 0
    and duplicate_record_count == 0
)

if not tax_rates_is_valid:
    raise ValueError(
        "TaxRates validation failed: "
        f"{invalid_record_count} incomplete rows, "
        f"{invalid_rate_count} invalid-rate rows, "
        f"{duplicate_record_count} duplicate rows."
    )


# ============================================================
# FINALISE DATAFRAME
# ============================================================

tax_rates_validation_summary = {
    "RowsImported": rows_imported,
    "Countries": tax_rates["Country Key"].nunique(),
    "Years": tax_rates["Year"].nunique(),
    "IncompleteRows": invalid_record_count,
    "InvalidRateRows": invalid_rate_count,
    "DuplicateRows": duplicate_record_count,
    "IsValid": tax_rates_is_valid,
}

tax_rates = (
    tax_rates
    .sort_values(
        by=[
            "Country",
            "Country Key",
            "Year",
        ],
        ascending=True,
        na_position="last",
    )
    .reset_index(drop=True)
)

# ============================================================
# TAX RATES VALIDATION OUTPUTS
# ============================================================

## This code block generates validation messages for the TaxRates dataframe, providing a summary of the validation results
## The messages are structured to provide both business and technical details for users to understand the validation outcomes.
## In the Excel application these messages are displayed to the user via the model log on the application home page.

if tax_rates_is_valid:

    tax_rates_status = (
        "✅ Tax rates loaded and validated successfully."
    )

    tax_rates_business_message = (
        "Country and year tax assumptions are ready for post-tax modelling."
    )

    tax_rates_technical_detail = (
        f"🟩 {tax_rates_validation_summary['RowsImported']:,} tax-rate rows imported and retained.\n"
        f"🟦 {tax_rates_validation_summary['Countries']:,} countries represented.\n"
        f"🟪 {tax_rates_validation_summary['Years']:,} years represented.\n"
        f"⬛ No incomplete, duplicate or invalid-rate records identified."
    )

else:

    tax_rates_status = (
        "❌ Tax rates validation failed."
    )

    tax_rates_business_message = (
        "Post-tax calculations cannot run until the tax-rate assumptions are corrected."
    )

    tax_rates_technical_detail = (
        f"🟥 {tax_rates_validation_summary['IncompleteRows']:,} incomplete rows found.\n"
        f"🟥 {tax_rates_validation_summary['InvalidRateRows']:,} rows contain rates outside the permitted range.\n"
        f"🟥 {tax_rates_validation_summary['DuplicateRows']:,} duplicate Country Key and Year rows found.\n"
        f"⬛ Review and correct the TaxRates table before running the scenario engine."
    )

tax_rates_status

# ============================================================
# PROFILES DATAFRAME
# ============================================================

## This code block sets up the Profiles dataframe by importing data from Excel, cleaning the column structure and field values, removing invalid records, validating unique IDs and case names, checking hierarchy completeness, and finalizing the dataframe for further processing.

profile_is_valid = False
profile_validation_error = ""
profile_duplicate_records = pd.DataFrame()

data_profile_tall = xl(
    "OGProfiles[#All]",
    headers=True
).copy()

rows_imported = len(data_profile_tall)


# ============================================================
# CLEAN COLUMN STRUCTURE
# ============================================================

## This code block cleans the column structure of the Profiles dataframe by stripping whitespace, removing brackets, renaming columns, and retaining only the required columns for further processing.
## The square brackets arise due to the DAX query used to extract the data from the Power BI model, which returns column names in a specific format. The code removes these brackets to standardize the column names for easier manipulation and analysis.

data_profile_tall.columns = (
    data_profile_tall.columns
    .astype(str)
    .str.strip()
    .str.removeprefix("[")
    .str.removesuffix("]")
)

data_profile_tall = data_profile_tall.rename(
    columns={"Index": "ID"}
)

required_columns = [
    "ID",
    "Case",
    "Metric",
    "Year",
    "Value",
]

data_profile_tall = data_profile_tall[
    required_columns
].copy()


# ============================================================
# CLEAN FIELD VALUES
# ============================================================

## This code block cleans the field values in the Profiles dataframe by converting columns to appropriate data types, stripping whitespace, and replacing empty strings with NaN values.

for col in ["Case", "Metric"]:
    data_profile_tall[col] = (
        data_profile_tall[col]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

for col in ["ID", "Year", "Value"]:
    data_profile_tall[col] = pd.to_numeric(
        data_profile_tall[col],
        errors="coerce"
    )


# ============================================================
# REMOVE INVALID RECORDS
# ============================================================

invalid_record_mask = data_profile_tall[
    ["ID", "Case", "Metric", "Year"]
].isna().any(axis=1)

invalid_records_removed = int(
    invalid_record_mask.sum()
)

data_profile_tall = data_profile_tall.loc[
    ~invalid_record_mask
].copy()


# ============================================================
# CLEAN PROFILE VALUES
# ============================================================

values_defaulted_to_zero = int(
    data_profile_tall["Value"].isna().sum()
)

data_profile_tall["Value"] = (
    data_profile_tall["Value"]
    .fillna(0)
)

data_profile_tall["ID"] = (
    data_profile_tall["ID"]
    .astype(int)
)

data_profile_tall["Year"] = (
    data_profile_tall["Year"]
    .astype(int)
)

TOLERANCE = 1e-9

floating_noise_mask = (
    data_profile_tall["Value"].ne(0)
    & data_profile_tall["Value"].abs().lt(TOLERANCE)
)

floating_values_reset = int(
    floating_noise_mask.sum()
)

data_profile_tall.loc[
    floating_noise_mask,
    "Value"
] = 0

data_profile_tall["Value"] = (
    data_profile_tall["Value"]
    .round(6)
)


# ============================================================
# VALIDATE MODELLING KEY
# ============================================================

profile_key = [
    "ID",
    "Metric",
    "Year",
]

duplicate_rows = data_profile_tall.duplicated(
    subset=profile_key,
    keep=False
)

if duplicate_rows.any():

    profile_duplicate_records = (
        data_profile_tall.loc[
            duplicate_rows,
            [
                "ID",
                "Case",
                "Metric",
                "Year",
                "Value",
            ]
        ]
        .sort_values(profile_key)
        .reset_index(drop=True)
    )

    profile_validation_error = (
        f"{len(profile_duplicate_records):,} profile rows contain "
        "duplicate ID, Metric and Year combinations."
    )

else:

    profile_is_valid = True


# ============================================================
# FINALISE DATAFRAME
# ============================================================

data_profile_tall = (
    data_profile_tall
    .sort_values(profile_key)
    .reset_index(drop=True)
)

profile_validation_summary = {
    "RowsImported": rows_imported,
    "RowsRetained": len(data_profile_tall),
    "InvalidRecordsRemoved": invalid_records_removed,
    "ValuesDefaultedToZero": values_defaulted_to_zero,
    "FloatingValuesReset": floating_values_reset,
    "Cases": data_profile_tall["ID"].nunique(),
    "Metrics": data_profile_tall["Metric"].nunique(),
    "YearMin": data_profile_tall["Year"].min(),
    "YearMax": data_profile_tall["Year"].max(),
    "DuplicateRows": int(duplicate_rows.sum()),
}

profile_is_valid

# ============================================================
# PROFILE VALIDATION MESSAGES
# ============================================================#

## This code block generates validation messages for the Profiles dataframe, providing a summary of the validation results, including the number of valid rows retained, invalid records removed, duplicate records found, and any values defaulted to zero or reset due to floating-point noise.
## Results are returned to the user via the model log on the application home page, providing both business and technical details for users to understand the validation outcomes.

if profile_is_valid:

    profile_validation_status = (
        "✅ Financial profiles loaded and validated successfully."
    )

    profile_validation_business_message = (
        f"Financial profiles for "
        f"{profile_validation_summary['Cases']:,} cases are ready "
        f"for scenario modelling across the "
        f"{profile_validation_summary['YearMin']}–"
        f"{profile_validation_summary['YearMax']} planning horizon."
    )

    profile_validation_technical_detail = (
        f"🟩 {profile_validation_summary['RowsRetained']:,} valid rows retained "
        f"from {profile_validation_summary['RowsImported']:,} imported.\n"
        f"🟦 {profile_validation_summary['InvalidRecordsRemoved']:,} invalid records removed.\n"
        f"🟪 {profile_validation_summary['ValuesDefaultedToZero']:,} blank or invalid values defaulted to zero.\n"
        f"⬛ {profile_validation_summary['FloatingValuesReset']:,} near-zero values reset.\n"
        f"📊 {profile_validation_summary['Cases']:,} cases and "
        f"{profile_validation_summary['Metrics']:,} metrics validated."
    )

else:

    profile_validation_status = (
        "❌ Financial profile validation failed."
    )

    profile_validation_business_message = (
        "Duplicate financial profile records were identified. "
        "Each case must contain only one value for each metric and year "
        "before the scenario engine can run."
    )

    profile_validation_technical_detail = (
        f"🟥 {profile_validation_summary['DuplicateRows']:,} duplicate profile rows identified.\n"
        f"🟧 Duplicate ID, Metric and Year combinations detected.\n"
        f"⬛ Scenario engine processing has been blocked.\n"
        f"📄 Review the duplicate profile output and correct the source data."
    )

profile_validation_status

