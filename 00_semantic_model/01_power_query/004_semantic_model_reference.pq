// ========================================================
// SEMANTIC MODEL REFERENCE DATA
// ========================================================
//
// Purpose
// -------
// This module contains the supporting reference, hierarchy and
// assumption datasets used by the Upstream Portfolio Scenario
// Modelling Framework.
//
// Unlike the principal transaction-processing pipelines, these queries
// primarily provide controlled descriptive attributes, hierarchy
// structures and modelling assumptions that are used to classify,
// enrich and calculate the scenario datasets.
//
// The module includes:
//
// 1/ Financial Entity reference data
//    Retrieves the core Financial Entity dimension and associated
//    hierarchy structures used throughout the modelling framework.
//
// 2/ Hierarchy quality control
//    Applies deterministic de-duplication to the Financial Entity
//    hierarchy and exposes duplicate checks for validation.
//
// 3/ Manual Financial Entity integration
//    Appends approved manually supplied Financial Entity metadata to
//    the governed system dimension before hierarchy enrichment.
//
// 4/ Planning reference dimensions
//    Provides Main Plan / Option, Renewal and Option Tag reference
//    structures used in downstream modelling and reporting.
//
// 5/ Plan Type derivation support
//    Main Plan Option and Renewal Selection attributes are consumed by
//    the controlled semantic-model-to-Excel interface to derive the
//    business-facing Plan Type classification:
//
//        Manual
//        Main Plan
//        Selected Option
//        Not Selected Option
//
//    This keeps the classification logic explicit and consistent rather
//    than requiring users to infer planning status directly from source
//    system codes.
//
// 6/ Tax assumptions
//    Retrieves controlled Effective Tax Rate (ETR) and Cash Tax Rate
//    (CTR) assumptions and reshapes them into the Country × Year
//    structure consumed by the Python post-tax modelling layer.
//
// Cross-module dependencies
// -------------------------
// ManualMetadata : Controlled Manual Profile Integration module
//
// Downstream dependencies
// -----------------------
// Financial Entity dimensions:
//     Controlled Semantic Model to Excel Interface
//     Financial Entity to Modelling Case Translation
//     Scenario reporting
//
// Planning dimensions:
//     DAX / OLE DB Plan Type derivation
//
// Tax rates:
//     Python Scenario Modelling Engine — post-tax calculations
//
// Design principles:
// Governed reference data | Consistent classification |
// Reusable dimensions | Controlled assumptions |
// Source traceability | Data quality by design |
// Explicit business classification | Separation of concerns
//
// Security
// --------
// Production host names, database names, SharePoint locations and
// environment-specific identifiers have been removed from this
// repository version and replaced with descriptive placeholders.
//
// ========================================================


// ========================================================
// ## Dim_Fin_Ent_IM_Raw
// ========================================================
//
// Purpose:
// Retrieves the governed Financial Entity master-data dimension used
// to enrich transaction and modelling datasets.
//
// Processing:
// 1/ Connects to the governed enterprise database
// 2/ Retrieves the Financial Entity dimension view
// 3/ Removes records without an assigned Country
// 4/ Returns the controlled Financial Entity reference dataset
//
// ========================================================

let
    Source =
        Sql.Database(
            "<Your Host Name>",
            "<Your Database Name>"
        ),

    Navigation =
        Source{
            [
                Schema = "<Your Dimension Schema>",
                Item = "<Your Financial Entity Dimension View>"
            ]
        }[Data],

    FilteredRows =
        Table.SelectRows(
            Navigation,
            each [Country] <> null
        )

in
    FilteredRows


// ========================================================
// ## Dim_Fin_Ent_Hier_IM_Raw
// ========================================================
//
// Purpose:
// Retrieves and de-duplicates the Financial Entity hierarchy used to
// provide consistent hierarchy attributes to the semantic model.
//
// A deterministic ROW_NUMBER rule ensures that no more than one
// hierarchy record is returned for each Financial Entity Region key.
//
// Processing:
// 1/ Connects to the governed enterprise database
// 2/ Retrieves the Financial Entity hierarchy view
// 3/ Partitions records by Financial_Entity_Region
// 4/ Assigns a deterministic row number within each partition
// 5/ Retains one hierarchy row per Financial Entity Region
//
// ========================================================

let
    Source =
        Sql.Database(
            "<Your Host Name>",
            "<Your Database Name>",
            [
                Query =
                "
                SELECT *
                FROM (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (
                            PARTITION BY Financial_Entity_Region
                            ORDER BY
                                CASE
                                    WHEN Financial_Entity_Region IS NOT NULL THEN 0
                                    ELSE 1
                                END,
                                (SELECT NULL)
                        ) AS rn
                    FROM <Your Dimension Schema>.<Your Financial Entity Hierarchy View>
                ) t
                WHERE rn = 1
                "
            ]
        )

in
    Source


// ========================================================
// ## Fin_Ent_Hier_Dupe_Check
// ========================================================
//
// Purpose:
// Validates that the de-duplicated Financial Entity hierarchy contains
// exactly one record for each Financial_Entity_Region key.
//
// Any rows returned by this query represent hierarchy exceptions that
// require investigation.
//
// Processing:
// 1/ Groups the hierarchy by Financial_Entity_Region
// 2/ Counts records per key
// 3/ Returns only keys where the count is not equal to one
//
// Expected result:
// Zero rows.
//
// ========================================================

let
    Source =
        DIM_FIN_ENT_HIER_IM_RAW,

    GroupedRows =
        Table.Group(
            Source,
            {"Financial_Entity_Region"},
            {
                {
                    "Count",
                    each Table.RowCount(_),
                    Int64.Type
                }
            }
        ),

    FilteredRows =
        Table.SelectRows(
            GroupedRows,
            each [Count] <> 1
        )

in
    FilteredRows


// ========================================================
// ## Dim_Financial_Entity_ADL
// ========================================================
//
// Purpose:
// Produces the integrated Financial Entity dimension used by the
// semantic model.
//
// The query combines governed system Financial Entities with approved
// manual Financial Entity metadata before enriching the resulting
// population with hierarchy attributes.
//
// Processing:
// 1/ Starts from the governed Financial Entity dimension
// 2/ Removes manual-feed audit fields not required in the dimension
// 3/ Appends approved manually supplied Financial Entity metadata
// 4/ Joins the combined population to the de-duplicated hierarchy
// 5/ Expands the required hierarchy levels
// 6/ Returns the integrated Financial Entity dimension
//
// ========================================================

let
    // ========================================================
    // SOURCE TABLES
    // ========================================================
    FinancialEntityDimension =
        DIM_FIN_ENT_IM_RAW,

    ManualFinancialEntities =
        Table.RemoveColumns(
            ManualMetadata,
            {
                "CaseDescription",
                "SourceFileName",
                "ManualFeedFlag"
            },
            MissingField.Ignore
        ),

    // ========================================================
    // APPEND SYSTEM AND MANUAL FINANCIAL ENTITIES
    // ========================================================
    AppendedFinancialEntities =
        Table.Combine(
            {
                FinancialEntityDimension,
                ManualFinancialEntities
            }
        ),

    // ========================================================
    // JOIN TO FINANCIAL ENTITY HIERARCHY
    // ========================================================
    MergedFinancialEntityHierarchy =
        Table.NestedJoin(
            AppendedFinancialEntities,
            {"Financial_Entity"},
            DIM_FIN_ENT_HIER_IM_RAW,
            {"Financial_Entity_Region"},
            "FinancialEntityHierarchy",
            JoinKind.LeftOuter
        ),

    // ========================================================
    // EXPAND HIERARCHY LEVELS
    // ========================================================
    ExpandedFinancialEntityHierarchy =
        Table.ExpandTableColumn(
            MergedFinancialEntityHierarchy,
            "FinancialEntityHierarchy",
            {
                "Level_01_Text",
                "Level_02_Text",
                "Level_03_Text",
                "Level_04_Text",
                "Level_05_Text",
                "Level_06_Text",
                "Level_07_Text"
            },
            {
                "Level_01_Text",
                "Level_02_Text",
                "Level_03_Text",
                "Level_04_Text",
                "Level_05_Text",
                "Level_06_Text",
                "Level_07_Text"
            }
        )

in
    ExpandedFinancialEntityHierarchy


// ========================================================
// ## Dim_Main_Plan_Option_ADL
// ========================================================
//
// Purpose:
// Retrieves the governed Main Plan / Option reference dimension and
// extends it with the controlled manual-feed classification.
//
// The additional "Z" = "Manual" member allows manually supplied
// profiles to participate in the same downstream planning and reporting
// structures as system-sourced profiles.
//
// This dimension also contributes to the downstream Plan Type
// classification used by the Excel modelling application.
//
// ========================================================

let
    Source =
        Sql.Database(
            "<Your Host Name>",
            "<Your Database Name>"
        ),

    Navigation =
        Source{
            [
                Schema = "<Your Dimension Schema>",
                Item = "<Your Main Plan Option Dimension View>"
            ]
        }[Data],

    ManualEntry =
        #table(
            type table
            [
                MainPlan_Option = text,
                MainPlan_Option_Text = text
            ],
            {
                {"Z", "Manual"}
            }
        ),

    Combined =
        Table.Combine(
            {
                Navigation,
                ManualEntry
            }
        )

in
    Combined


// ========================================================
// ## Dim_Renewal_ADL
// ========================================================
//
// Purpose:
// Retrieves the governed Renewal Selection reference dimension.
//
// Renewal Selection is used alongside Main Plan Option in the
// downstream semantic-model interface to distinguish selected and
// non-selected modelling options.
//
// ========================================================

let
    Source =
        Sql.Database(
            "<Your Host Name>",
            "<Your Database Name>"
        ),

    Navigation =
        Source{
            [
                Schema = "<Your Dimension Schema>",
                Item = "<Your Renewal Selection Dimension View>"
            ]
        }[Data]

in
    Navigation


// ========================================================
// ## Dim_OptionTag_Manual
// ========================================================
//
// Purpose:
// Provides the controlled Option Tag reference mapping used by the
// modelling framework.
//
// This table is maintained directly within Power Query because the
// required mapping is small, stable and specific to the modelling
// purpose.
//
// ========================================================

let
    ResultTable =
        #table(
            {
                "Option_Tag",
                "Option_Tag_Text"
            },
            {
                {"04", "Unassigned Option"},
                {"03", "Exploration Option"},
                {"02", "ADP Options"},
                {"01", "Main Plan"}
            }
        )

in
    ResultTable


// ========================================================
// ## Tax_Rates
// ========================================================
//
// Purpose:
// Prepares the controlled country and year tax assumptions consumed by
// the Python post-tax scenario engine.
//
// The source workbook contains separate Effective Tax Rate (ETR) and
// Cash Tax Rate (CTR) tables. These are combined and reshaped into one
// Country × Year record containing both rates.
//
// Processing:
// 1/ Retrieves the controlled tax-helper workbook
// 2/ Extracts the ETR and CTR source tables
// 3/ Tags each table with its corresponding rate type
// 4/ Appends ETR and CTR records
// 5/ Standardises column names
// 6/ Removes supporting fields not required downstream
// 7/ Converts year columns into a tall structure
// 8/ Pivots rate type to create ETR and CTR columns
// 9/ Applies final data types
// 10/ Returns the Country × Year tax-rate dataset
//
// Downstream use:
// The Python engine joins these assumptions to Underlying RCOP by
// Country Key and Year to derive Tax Charge, Cash Tax Payment,
// Post-Tax RCOP and Post-Tax Cash Flow.
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
                Name = "<Your Tax Helper Workbook.xlsm>",
                #"Folder Path" =
                    "<Your Data Input Folder Path>"
            ]
        }[Content],

    ImportedWorkbook =
        Excel.Workbook(
            FileContent,
            null,
            true
        ),

    ETR_Source =
        ImportedWorkbook{
            [
                Item = "ETR_Tbl",
                Kind = "Table"
            ]
        }[Data],

    ETR =
        Table.AddColumn(
            ETR_Source,
            "Rate Type",
            each "ETR",
            type text
        ),

    CTR_Source =
        ImportedWorkbook{
            [
                Item = "CTR_tbl",
                Kind = "Table"
            ]
        }[Data],

    CTR =
        Table.AddColumn(
            CTR_Source,
            "Rate Type",
            each "CTR",
            type text
        ),

    ETR_CTR =
        Table.Combine(
            {
                ETR,
                CTR
            }
        ),

    CleanColumnNames =
        Table.TransformColumnNames(
            ETR_CTR,
            each
                Text.Trim(
                    Text.Trim(_),
                    {"[", "]"}
                )
        ),

    RemovedSupportingColumns =
        Table.RemoveColumns(
            CleanColumnNames,
            {
                "Index",
                "Count Check"
            }
        ),

    UnpivotYears =
        Table.UnpivotOtherColumns(
            RemovedSupportingColumns,
            {
                "Country Key",
                "Country",
                "Rate Type"
            },
            "Year",
            "Rate"
        ),

    PivotRateType =
        Table.Pivot(
            UnpivotYears,
            List.Distinct(
                UnpivotYears[Rate Type]
            ),
            "Rate Type",
            "Rate",
            List.Sum
        ),

    SetDataTypes =
        Table.TransformColumnTypes(
            PivotRateType,
            {
                {"Country Key", type text},
                {"Country", type text},
                {"Year", type text},
                {"ETR", Percentage.Type},
                {"CTR", Percentage.Type}
            }
        )

in
    SetDataTypes