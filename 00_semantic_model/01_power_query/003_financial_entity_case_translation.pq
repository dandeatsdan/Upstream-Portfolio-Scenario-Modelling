// ========================================================
// CONTROLLED FINANCIAL ENTITY TO MODELLING CASE TRANSLATION
// ========================================================
//
// Purpose
// -------
// This module provides the controlled translation between the
// Financial Entity grain used by the governed source data and the
// Modelling Case grain used by the scenario modelling application.
//
// The translation is maintained through a controlled Excel template.
// Users are presented with valid Financial Entity reference data and
// can define the aggregation level used to construct modelling cases,
// for example Region, Country, Area, Field Group, Building Block or
// individual Financial Entity.
//
// The template also supports an explicit override where a standard
// aggregation does not adequately represent the required modelling
// case. This keeps the business grouping decision visible and
// reviewable rather than embedding it within downstream code.
//
// The resulting translation table provides a stable relationship
// between:
// - Financial Entity key;
// - source hierarchy attributes;
// - selected aggregation method;
// - generated / overridden modelling-case definition; and
// - Plan Type.
//
// The mapping is subsequently joined to the integrated transaction
// dataset so that source and manually supplied Financial Entity
// profiles are assigned to the modelling grain consumed by the
// Excel scenario configuration and Python engine.
//
// User workflow
// -------------
// 1/ The controlled translation workbook is populated with valid
//    Financial Entity reference data.
//
// 2/ The user selects the required aggregation method for each
//    Financial Entity.
//
// 3/ The workbook automatically proposes the resulting modelling
//    case using the selected hierarchy level.
//
// 4/ Where required, the user can enter an explicit override.
//
// 5/ The resulting modelling-case assignment is validated and stored
//    within the controlled translation table.
//
// 6/ Power Query retrieves the completed mapping and joins it to the
//    integrated financial transaction dataset.
//
// Cross-module dependencies
// -------------------------
// TRANS_SYSTEM   : Controlled Transaction Scope module
// TRANS_DERIVED  : Controlled Transaction Scope module
// ManualProfiles : Controlled Manual Profile Integration module
//
// Design principles:
// Controlled translation | Source traceability | Human accountability |
// Complete population | Consistent classification | Stable identity |
// Transparent overrides | Separation of source and modelling grain
//
// Security
// --------
// Production SharePoint locations and workbook paths have been removed
// from this repository version and replaced with descriptive
// placeholders.
//
// ========================================================


// ========================================================
// ## Map_FE_to_Case
// ========================================================
//
// Purpose:
// Retrieves the completed Financial Entity to Modelling Case
// translation maintained in the controlled Excel template.
//
// Processing:
// 1/ Connects to the controlled SharePoint location
// 2/ Retrieves the Financial Entity translation workbook
// 3/ Opens the workbook
// 4/ Retrieves the controlled Case Listing table
// 5/ Standardises column names returned by the Excel table
// 6/ Returns the final Financial Entity to Modelling Case mapping
//
// ========================================================

let
    Source =
        SharePoint.Files(
            "<Your SharePoint Site URL>",
            [ApiVersion = 15]
        ),

    FileContent =
        Source{
            [
                Name = "<Your Financial Entity Translation Workbook.xlsm>",
                #"Folder Path" = "<Your Data Input Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            FileContent,
            null,
            true
        ),

    CaseListing =
        ImportedWorkbook{
            [
                Item = "OGLTPDataPipeline_CaseListing",
                Kind = "Table"
            ]
        }[Data],

    CleanColumnNames =
        Table.TransformColumnNames(
            CaseListing,
            each
                Text.Trim(
                    Text.Trim(_),
                    {"[", "]"}
                )
        )

in
    CleanColumnNames


// ========================================================
// ## Trans_Fin_ADL — MODELLING CASE ASSIGNMENT
// ========================================================
//
// Purpose:
// Applies the controlled Financial Entity to Modelling Case mapping
// to the final integrated transaction population.
//
// This represents the hand-off from source-data preparation into the
// modelling grain used by the scenario application.
//
// Processing:
// 1/ Combines approved system-source and calculated-member transactions
// 2/ Appends approved manual profiles
// 3/ Joins each Financial Entity to the controlled translation table
// 4/ Expands the assigned Modelling Case
// 5/ Returns the transaction population at the required modelling grain
//
// Note:
// This logic is also represented within the Controlled Transaction
// Scope module because it forms the final integration step of that
// pipeline. It is repeated here deliberately to make the dependency
// between transaction preparation and case translation explicit.
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