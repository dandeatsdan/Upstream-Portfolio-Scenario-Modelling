// ========================================================
// CONTROLLED TRANSACTION SCOPE & CALCULATED MEMBER DERIVATION
// ========================================================
//
// Purpose
// -------
// This module prepares the controlled transaction dataset used by
// the Upstream Portfolio Scenario Modelling Framework.
//
// It deliberately reduces the wider enterprise transaction population
// to the accounts, years, entities and planning data required for the
// approved modelling purpose. It then derives additional modelling
// metrics through controlled account-routing and weighting rules.
//
// The module performs six principal activities:
//
// 1/ Account control tables
//    Retrieves the approved system accounts, calculated-member
//    definitions, calculation routing logic and metric sort metadata.
//
// 2/ System account scope
//    Restricts the source-account population to those explicitly
//    required by the modelling framework.
//
// 3/ Controlled source extraction
//    Retrieves the required transaction population from the governed
//    enterprise data source using defined planning, year and entity
//    filters.
//
// 4/ System transaction construction
//    Retains transactions associated with approved source accounts.
//
// 5/ Calculated-member derivation
//    Applies explicit routing weights to source accounts and aggregates
//    the resulting values into defined derived modelling metrics.
//
// 6/ Final transaction integration
//    Combines system transactions, calculated members and approved
//    manual profiles before assigning each Financial Entity to its
//    downstream Modelling Case.
//
// Cross-module dependencies
// -------------------------
// ManualProfiles  : Controlled Manual Profile Integration module
// Map_FE_to_Case  : Financial Entity to Modelling Case Translation module
//
// Design principles:
// Purpose limitation | Data minimisation | Controlled scope |
// Transparent derivation | Consistent calculation | Source traceability |
// Early transformation | Reusable logic
//
// Security
// --------
// Production connection details, SharePoint locations, database names,
// schema names and planning identifiers have been removed from this
// repository version and replaced with descriptive placeholders.
//
// ========================================================


// ========================================================
// ## Accounts_System
// ========================================================
//
// Purpose:
// Retrieves the approved system-account definitions used to determine
// which enterprise source accounts are available to the modeller.
//
// Processing:
// 1/ Connects to the controlled account-definition workbook
// 2/ Retrieves the SystemMembers table
// 3/ Retains only accounts approved for the modelling scope
// 4/ Removes the temporary scope-control field
//
// ========================================================

let
    Source =
        SharePoint.Files(
            "<Your SharePoint Site URL>",
            [ApiVersion = 15]
        ),

    AccountWorkbook =
        Source{
            [
                Name = "<Your Account Mapping Workbook.xlsx>",
                #"Folder Path" = "<Your Account Mapping Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            AccountWorkbook
        ),

    SystemMembers_Table =
        ImportedWorkbook{
            [
                Item = "SystemMembers",
                Kind = "Table"
            ]
        }[Data],

    FilteredScope =
        Table.SelectRows(
            SystemMembers_Table,
            each [MVP Scope] = "Yes"
        ),

    RemovedScopeColumn =
        Table.RemoveColumns(
            FilteredScope,
            {"MVP Scope"}
        )

in
    RemovedScopeColumn


// ========================================================
// ## Accounts_Derived_Names
// ========================================================
//
// Purpose:
// Retrieves the approved calculated-member definitions used to identify
// the derived metrics created by the transaction-calculation pipeline.
//
// Processing:
// 1/ Connects to the controlled account-definition workbook
// 2/ Retrieves the CalcMembers table
// 3/ Standardises the Account ID data type
// 4/ Identifies records as calculated members
// 5/ Retains only members approved for the modelling scope
// 6/ Removes the temporary scope-control field
//
// ========================================================

let
    Source =
        SharePoint.Files(
            "<Your SharePoint Site URL>",
            [ApiVersion = 15]
        ),

    AccountWorkbook =
        Source{
            [
                Name = "<Your Account Mapping Workbook.xlsx>",
                #"Folder Path" = "<Your Account Mapping Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            AccountWorkbook
        ),

    CalcMembers_Table =
        ImportedWorkbook{
            [
                Item = "CalcMembers",
                Kind = "Table"
            ]
        }[Data],

    ChangedType =
        Table.TransformColumnTypes(
            CalcMembers_Table,
            {
                {"Account ID", type text}
            }
        ),

    AddedType =
        Table.AddColumn(
            ChangedType,
            "Type",
            each "Calc",
            type text
        ),

    FilteredScope =
        Table.SelectRows(
            AddedType,
            each [MVP Scope] = "Yes"
        ),

    RemovedScopeColumn =
        Table.RemoveColumns(
            FilteredScope,
            {"MVP Scope"}
        )

in
    RemovedScopeColumn


// ========================================================
// ## Accounts_Calc_Logics
// ========================================================
//
// Purpose:
// Retrieves the controlled calculation-routing table used to define
// how source accounts contribute to calculated modelling metrics.
//
// The routing structure provides the explicit relationship between
// source accounts, calculated members and calculation weights.
//
// Processing:
// 1/ Connects to the controlled account-definition workbook
// 2/ Retrieves the calculation-routing table
// 3/ Standardises routing-key data types
// 4/ Retains only routing rules approved for the modelling scope
// 5/ Removes the temporary scope-control field
//
// ========================================================

let
    Source =
        SharePoint.Files(
            "<Your SharePoint Site URL>",
            [ApiVersion = 15]
        ),

    AccountWorkbook =
        Source{
            [
                Name = "<Your Account Mapping Workbook.xlsx>",
                #"Folder Path" = "<Your Account Mapping Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            AccountWorkbook
        ),

    FOX_Table =
        ImportedWorkbook{
            [
                Item = "FOX",
                Kind = "Table"
            ]
        }[Data],

    ChangedType =
        Table.TransformColumnTypes(
            FOX_Table,
            {
                {"CalcLineID", type text},
                {"ShortKey", type text}
            }
        ),

    FilteredScope =
        Table.SelectRows(
            ChangedType,
            each [MVP Scope] = "Yes"
        ),

    RemovedScopeColumn =
        Table.RemoveColumns(
            FilteredScope,
            {"MVP Scope"}
        )

in
    RemovedScopeColumn


// ========================================================
// ## Accounts_Sorting
// ========================================================
//
// Purpose:
// Retrieves the controlled metric metadata and sorting structure used
// downstream by the modelling and reporting framework.
//
// Processing:
// 1/ Connects to the controlled account-definition workbook
// 2/ Retrieves the Metric_Sorts table
// 3/ Retains only metrics approved for the modelling scope
// 4/ Removes the temporary scope-control field
//
// ========================================================

let
    Source =
        SharePoint.Files(
            "<Your SharePoint Site URL>",
            [ApiVersion = 15]
        ),

    AccountWorkbook =
        Source{
            [
                Name = "<Your Account Mapping Workbook.xlsx>",
                #"Folder Path" = "<Your Account Mapping Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            AccountWorkbook
        ),

    Metric_Sorts_Table =
        ImportedWorkbook{
            [
                Item = "Metric_Sorts",
                Kind = "Table"
            ]
        }[Data],

    FilteredScope =
        Table.SelectRows(
            Metric_Sorts_Table,
            each [MVP Scope] = "Yes"
        ),

    RemovedScopeColumn =
        Table.RemoveColumns(
            FilteredScope,
            {"MVP Scope"}
        )

in
    RemovedScopeColumn


// ========================================================
// ## Accounts_Needed
// ========================================================
//
// Purpose:
// Creates the final source-account inclusion list used to restrict the
// enterprise transaction dataset to accounts required by the modeller.
//
// This represents a key data-minimisation control: source transactions
// are only retained where their account has been explicitly identified
// as required.
//
// Processing:
// 1/ Starts from the controlled system-account definition
// 2/ Retains accounts marked as Needed
// 3/ Removes supporting metadata not required for transaction filtering
// 4/ Returns the final source-account key list
//
// ========================================================

let
    Source =
        ACCOUNTS_SYSTEM,

    FilterAccountsNeeded =
        Table.SelectRows(
            Source,
            each [Needed] = "Yes"
        ),

    Source_Final =
        Table.RemoveColumns(
            FilterAccountsNeeded,
            {
                "Account ID",
                "Description",
                "In FIN Data Flow",
                "Needed",
                "Type"
            }
        )

in
    Source_Final


// ========================================================
// ## Accounts_Derived
// ========================================================
//
// Purpose:
// Builds the controlled calculated-member routing structure used by
// TRANS_DERIVED.
//
// Each source account is associated with a calculated-member definition
// and weighting rule. The resulting table provides an explicit,
// inspectable calculation pathway from source metric to derived metric.
//
// Processing:
// 1/ Starts from the approved calculation-routing logic
// 2/ Removes supporting fields not required for calculation
// 3/ Joins each calculation line to its derived-member definition
// 4/ Expands the derived FullKey used as the output Account_Planning key
// 5/ Returns the calculation-routing structure
//
// ========================================================

let
    Source =
        ACCOUNTS_CALC_LOGICS,

    RemovedColumns =
        Table.RemoveColumns(
            Source,
            {
                "Notes",
                "ShortKey",
                "In FIN Data Flow"
            }
        ),

    MergedDerivedNames =
        Table.NestedJoin(
            RemovedColumns,
            {"CalcLineID"},
            ACCOUNTS_DERIVED_NAMES,
            {"Account ID"},
            "ACCOUNTS_DERIVED_NAMES",
            JoinKind.LeftOuter
        ),

    ExpandedDerivedNames =
        Table.ExpandTableColumn(
            MergedDerivedNames,
            "ACCOUNTS_DERIVED_NAMES",
            {"FullKey"},
            {"FullKey.1"}
        )

in
    ExpandedDerivedNames


// ========================================================
// ## Trans_Fin_IM_Raw
// ========================================================
//
// Purpose:
// Retrieves the controlled enterprise financial transaction population
// required for scenario modelling.
//
// The extraction deliberately applies the principal modelling filters
// at source to reduce unnecessary data transfer and processing.
//
// Processing:
// 1/ Connects to the governed enterprise SQL source
// 2/ Selects only fields required by downstream modelling
// 3/ Applies the approved planning submission and version filters
// 4/ Restricts the planning horizon to 2026–2040
// 5/ Restricts the population to the required time/data-set definitions
// 6/ Restricts Financial Entities to Oil and Gas
// 7/ Removes source zero values
// 8/ Normalises floating-point artefacts using a numerical tolerance
// 9/ Removes resulting zero/null transaction rows
//
// NOTE:
// Production host, database, schema, view and planning identifiers are
// intentionally replaced with placeholders in this repository version.
//
// ========================================================

let

    Source =
        Sql.Database(
            "<Your Host Name>",
            "<Your Database Name>"
        ),

    Query =
        Value.NativeQuery(
            Source,
            "
SELECT
    f.Account_Planning,
    f.Calendar_Year,
    f.Common_Key_Figure,
    f.Data_Set,
    f.Financial_Entity,
    f.Submission,
    f.Value_Type_for_Reporting,
    f.Version,
    f.Program,
    f.Building_Block,
    f.MainPlan_Option,
    f.Renewal_Selection,
    f.Option_Tag,
    f.[Fiscal_Year_/_Period],
    d.BP_Group_Entities_Text

FROM <Your Transaction Schema>.<Your Transaction View> AS f

INNER JOIN <Your Dimension Schema>.<Your Financial Entity View> AS d
    ON f.Financial_Entity = d.Financial_Entity

WHERE f.Submission = '<Your Submission ID>'
  AND CAST(f.Fiscal_Year AS INT) BETWEEN 2026 AND 2040
  AND f.Time_Data_Set = '<Your Time Data Set>'
  AND f.Version IN (
        '<Your Version 1>',
        '<Your Version 2>'
      )
  AND f.Data_Set = '<Your Data Set>'
  AND d.BP_Group_Entities_Text IN ('Oil', 'Gas')
  AND NOT (f.Common_Key_Figure = 0)
            ",
            null,
            [EnableFolding = true]
        ),

    // Numerical tolerance used to remove insignificant
    // floating-point artefacts from the source dataset.
    Tolerance =
        1e-9,

    NormalisedCommonKeyFigure =
        Table.TransformColumns(
            Query,
            {
                {
                    "Common_Key_Figure",
                    each
                        if _ = null then null
                        else if Number.Abs(_) < Tolerance then 0
                        else _,
                    type number
                }
            }
        ),

    RemovedZeroValues =
        Table.SelectRows(
            NormalisedCommonKeyFigure,
            each
                [Common_Key_Figure] <> null
                and [Common_Key_Figure] <> 0
        )

in
    RemovedZeroValues


// ========================================================
// ## Trans_System
// ========================================================
//
// Purpose:
// Creates the system-sourced transaction dataset used by the modeller.
//
// The query performs a controlled account-key join between the approved
// source-account population and the enterprise transaction extract,
// ensuring that only transactions associated with explicitly required
// modelling accounts are retained.
//
// Processing:
// 1/ Starts from the approved Accounts_Needed account list
// 2/ Joins to the controlled enterprise transaction population
// 3/ Expands the required transaction attributes
// 4/ Removes the temporary account-filter key
// 5/ Returns the system-sourced modelling transactions
//
// ========================================================

let
    Source =
        ACCOUNTS_NEEDED,

    MergedTransactions =
        Table.NestedJoin(
            Source,
            {"FullKey"},
            TRANS_FIN_IM_RAW,
            {"Account_Planning"},
            "TRANS_FIN_IM_RAW",
            JoinKind.LeftOuter
        ),

    ExpandedTransactions =
        Table.ExpandTableColumn(
            MergedTransactions,
            "TRANS_FIN_IM_RAW",
            {
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "Data_Set",
                "Financial_Entity",
                "Submission",
                "Value_Type_for_Reporting",
                "Version",
                "Program",
                "Building_Block",
                "MainPlan_Option",
                "Renewal_Selection",
                "Option_Tag",
                "Fiscal_Year_/_Period"
            },
            {
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "Data_Set",
                "Financial_Entity",
                "Submission",
                "Value_Type_for_Reporting",
                "Version",
                "Program",
                "Building_Block",
                "MainPlan_Option",
                "Renewal_Selection",
                "Option_Tag",
                "Fiscal_Year_/_Period"
            }
        ),

    RemovedFilterKey =
        Table.RemoveColumns(
            ExpandedTransactions,
            {"FullKey"}
        )

in
    RemovedFilterKey


// ========================================================
// ## Trans_Derived
// ========================================================
//
// Purpose:
// Creates calculated modelling transactions using the controlled
// account-routing and weighting structure.
//
// Source transaction values are joined to their approved calculation
// routes, multiplied by the defined routing weight and aggregated to
// the target calculated-member account.
//
// This preserves an explicit and reusable derivation pathway rather
// than embedding calculated-member logic within downstream reports
// or the Python scenario engine.
//
// Processing:
// 1/ Starts from the approved calculated-member routing structure
// 2/ Joins each routing source account to the enterprise transaction data
// 3/ Calculates the weighted transaction contribution
// 4/ Removes temporary routing/calculation fields
// 5/ Replaces the source account with the target calculated-member key
// 6/ Groups by the remaining transaction dimensions
// 7/ Sums weighted contributions into the calculated metric value
// 8/ Removes supporting fields no longer required downstream
//
// ========================================================

let
    Source =
        ACCOUNTS_DERIVED,

    MergedTransactions =
        Table.NestedJoin(
            Source,
            {"FullKey"},
            TRANS_FIN_IM_RAW,
            {"Account_Planning"},
            "TRANS_FIN_IM",
            JoinKind.LeftOuter
        ),

    ExpandedTransactions =
        Table.ExpandTableColumn(
            MergedTransactions,
            "TRANS_FIN_IM",
            {
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "Data_Set",
                "Financial_Entity",
                "Submission",
                "Value_Type_for_Reporting",
                "Version",
                "Program",
                "Building_Block",
                "MainPlan_Option",
                "Renewal_Selection",
                "Option_Tag",
                "Fiscal_Year_/_Period"
            },
            {
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "Data_Set",
                "Financial_Entity",
                "Submission",
                "Value_Type_for_Reporting",
                "Version",
                "Program",
                "Building_Block",
                "MainPlan_Option",
                "Renewal_Selection",
                "Option_Tag",
                "Fiscal_Year_/_Period"
            }
        ),

    AddedWeightedAmount =
        Table.AddColumn(
            ExpandedTransactions,
            "Weighted_Amount",
            each
                [Weight]
                * [Common_Key_Figure],
            type number
        ),

    RemovedCalculationFields =
        Table.RemoveColumns(
            AddedWeightedAmount,
            {
                "CalcLineID",
                "Weight",
                "Common_Key_Figure",
                "FullKey",
                "Account_Planning"
            }
        ),

    RenamedDerivedAccount =
        Table.RenameColumns(
            RemovedCalculationFields,
            {
                {"FullKey.1", "Account_Planning"}
            }
        ),

    GroupColumns =
        List.RemoveItems(
            Table.ColumnNames(
                RenamedDerivedAccount
            ),
            {"Weighted_Amount"}
        ),

    GroupedRows =
        Table.Group(
            RenamedDerivedAccount,
            GroupColumns,
            {
                {
                    "Common_Key_Figure",
                    each List.Sum(
                        [Weighted_Amount]
                    ),
                    type number
                }
            }
        ),

    RemovedSupportingFields =
        Table.RemoveColumns(
            GroupedRows,
            {
                "Count",
                "CalcandKey"
            }
        )

in
    RemovedSupportingFields


// ========================================================
// ## Trans_Fin_ADL
// ========================================================
//
// Purpose:
// Produces the final integrated transaction dataset consumed by the
// downstream semantic-model and scenario-modelling layers.
//
// The query combines:
// - approved system-source transactions;
// - controlled calculated-member transactions; and
// - approved manual modelling profiles.
//
// It then applies the Financial Entity to Modelling Case translation,
// providing the common modelling grain used by the Excel scenario
// configuration and Python engine.
//
// Cross-module dependencies:
// ManualProfiles : Controlled Manual Profile Integration
// Map_FE_to_Case : Financial Entity to Modelling Case Translation
//
// Processing:
// 1/ Appends system and derived transactions
// 2/ Appends approved manual profiles
// 3/ Joins Financial Entities to the controlled case translation
// 4/ Expands the assigned Modelling Case
// 5/ Returns the integrated modelling transaction dataset
//
// ========================================================

let
    Source =
        Table.Combine(
            {
                TRANS_SYSTEM,
                TRANS_DERIVED
            }
        ),

    AppendedManualProfiles =
        Table.Combine(
            {
                Source,
                ManualProfiles
            }
        ),

    MergedCaseTranslation =
        Table.NestedJoin(
            AppendedManualProfiles,
            {"Financial_Entity"},
            Map_FE_to_Case,
            {"Financial Entity Key"},
            "MAP_FE_TO_CASE",
            JoinKind.LeftOuter
        ),

    ExpandedCaseTranslation =
        Table.ExpandTableColumn(
            MergedCaseTranslation,
            "MAP_FE_TO_CASE",
            {"Modelling_Case"},
            {"Modelling_Case"}
        )

in
    ExpandedCaseTranslation