// ========================================================
// MANUAL DATA PIPELINE
// ========================================================
//
// Purpose
// -------
// This module provides the controlled ingestion pathway for
// approved manual modelling profiles that are not available
// through the primary system data source.
//
// Each approved Excel workbook contains:
// - a standard Input_Template table containing profile data; and
// - controlled workbook metadata held in defined names.
//
// The pipeline performs five principal activities:
//
// 1/ ManualFeedFiles
//    Discovers supported workbooks in the controlled SharePoint
//    location and assigns each file a surrogate Financial Entity key.
//
// 2/ fnExtractManualProfiles
//    Validates and transforms each workbook's profile data into the
//    standard tall transaction structure used by the modelling dataset.
//
// 3/ ManualProfiles
//    Executes the profile extraction function across all approved
//    workbooks and combines the results into one transaction dataset.
//
// 4/ fnExtractManualMetadata
//    Extracts the controlled dimensional metadata associated with
//    each manual modelling case.
//
// 5/ ManualMetaData
//    Executes the metadata extraction function across all approved
//    workbooks and aligns the results to the Financial Entity
//    dimension structure.
//
// Together, these components allow approved manual profiles to enter
// the same downstream modelling framework as system-sourced profiles
// while preserving source identification, controlled metadata,
// surrogate entity identity and a standardised downstream schema.
//
// Design principles:
// Controlled metadata | Surrogate entity identity | Standardised schema |
// Source traceability | Data quality by design | Governed extensibility |
// Reusable ingestion | Seamless system/manual integration
//
// ========================================================


// ========================================================
// ## ManualFeedFiles
// ========================================================

// This query is used to retrieve the list of manual feed files from the SharePoint folder
//
// The query performs the following steps:
// 1/ Retrieves all files from the SharePoint folder
// 2/ Filters to the controlled manual feed folder      
// 3/ Retains only supported Excel workbooks (.xlsx, .xlsm) and excludes temporary files (~$)
// 4/ Sorts the files by creation date and name to ensure consistent key assignment
// 5/ Assigns a dummy FinancialEntityKey to each file, starting from 900
// 6/ Retains only the columns required downstream
// 7/ Renames columns to friendlier names
// 8/ Sets the final data types

let
    // ========================================================
    // SHAREPOINT SOURCE
    // ========================================================
    Source =
        SharePoint.Files(
            <Your SharePoint Site URL>, ## Redacted for security reasons
            [ApiVersion = 15]
        ),

    TargetFolder =
        <  Your Target Folder Path in SharePoint>,

    // ========================================================
    // FILTER TO THE CONTROLLED MANUAL FEED FOLDER
    // ========================================================
    FilteredFolder =
        Table.SelectRows(
            Source,
            each [Folder Path] = TargetFolder
        ),

    // ========================================================
    // RETAIN SUPPORTED EXCEL WORKBOOKS ONLY
    // ========================================================
    FilteredExcelFiles =
        Table.SelectRows(
            FilteredFolder,
            each
                List.Contains(
                    {".xlsx", ".xlsm"},
                    Text.Lower([Extension])
                )
                and not Text.StartsWith([Name], "~$")
        ),

    // ========================================================
    // SORT FILES BEFORE ASSIGNING KEYS
    // Earliest-created workbook receives the lowest key
    // ========================================================
    SortedFiles =
        Table.Sort(
            FilteredExcelFiles,
            {
                {"Date created", Order.Ascending},
                {"Name", Order.Ascending}
            }
        ),

    // ========================================================
    // ASSIGN DUMMY FINANCIAL ENTITY KEYS
    // ========================================================
    AddedFinancialEntityKey =
        Table.AddIndexColumn(
            SortedFiles,
            "FinancialEntityKey",
            9000000001,
            1,
            Int64.Type
        ),

    // ========================================================
    // RETAIN ONLY THE COLUMNS REQUIRED DOWNSTREAM
    // ========================================================
    SelectedColumns =
        Table.SelectColumns(
            AddedFinancialEntityKey,
            {
                "FinancialEntityKey",
                "Name",
                "Extension",
                "Folder Path",
                "Date created",
                "Date modified",
                "Content"
            }
        ),

    // ========================================================
    // FRIENDLIER COLUMN NAMES
    // ========================================================
    RenamedColumns =
        Table.RenameColumns(
            SelectedColumns,
            {
                {"Name", "SourceFileName"},
                {"Date created", "SourceCreatedDate"},
                {"Date modified", "SourceModifiedDate"}
            }
        ),

    // ========================================================
    // FINAL DATA TYPES
    // ========================================================
    ChangedTypes =
        Table.TransformColumnTypes(
            RenamedColumns,
            {
                {"FinancialEntityKey",  Int64.Type},
                {"SourceFileName", type text},
                {"Extension", type text},
                {"Folder Path", type text},
                {"SourceCreatedDate", type datetimezone},
                {"SourceModifiedDate", type datetimezone}
            }
        )
in
    ChangedTypes

// ========================================================
// ## fnExtractManualProfiles
// ========================================================

// This function is used to extract the manual feed profiles from the input template in the manual feed files
//
// It works by performing the following steps:
// 1/ Opens the workbook and retrieves the contents of the "Input_Template" table
// 2/ Validates the account planning keys against the ACCOUNTS_SORTING table
// 3/ Standardises the account column name to "Account_Planning"
// 4/ Removes non-transaction columns (Metric, Notes, ValidatedFullKey)
// 5/ Converts the year columns to a tall format (Calendar_Year, Common_Key_Figure)
// 6/ Adds the FinancialEntityKey and SourceFileName for traceability
// 7/ Adds a manual feed flag column for traceability (MainPlan_Option = "Z")
// 8/ Applies the final data types and column order
// 9/ Returns the final table of manual feed profiles

(
    FileContent as binary,
    FinancialEntityKey as number,
    SourceFileName as text
)
as table =>

let
    // ========================================================
    // OPEN WORKBOOK
    // ========================================================
    WorkbookContents =
        Excel.Workbook(
            FileContent,
            null,
            true
        ),

    // ========================================================
    // EXTRACT STANDARD INPUT TABLE
    // ========================================================
    InputTemplate =
        WorkbookContents{
            [
                Item = "Input_Template",
                Kind = "Table"
            ]
        }[Data],

    // ========================================================
    // VALIDATE ACCOUNT PLANNING KEYS
    // ========================================================
    MergedAccountMapping =
        Table.NestedJoin(
            InputTemplate,
            {"ID"},
            ACCOUNTS_SORTING,
            {"FullKey"},
            "AccountMapping",
            JoinKind.LeftOuter
        ),

    ExpandedAccountMapping =
        Table.ExpandTableColumn(
            MergedAccountMapping,
            "AccountMapping",
            {"FullKey"},
            {"ValidatedFullKey"}
        ),

    ValidAccountRows =
        Table.SelectRows(
            ExpandedAccountMapping,
            each [ValidatedFullKey] <> null
        ),

    // ========================================================
    // STANDARDISE ACCOUNT COLUMN
    // ========================================================
    RenamedAccountColumn =
        Table.RenameColumns(
            ValidAccountRows,
            {
                {"ID", "Account_Planning"}
            }
        ),

    // ========================================================
    // REMOVE NON-TRANSACTION COLUMNS
    // ========================================================
    RemovedSupportingColumns =
        Table.RemoveColumns(
            RenamedAccountColumn,
            {
                "Metric",
                "Notes",
                "ValidatedFullKey"
            },
            MissingField.Ignore
        ),

    // ========================================================
    // CONVERT YEAR COLUMNS TO TALL FORMAT
    // ========================================================
    UnpivotedProfiles =
        Table.UnpivotOtherColumns(
            RemovedSupportingColumns,
            {"Account_Planning"},
            "Calendar_Year",
            "Common_Key_Figure"
        ),

    // ========================================================
    // ADD FINANCIAL ENTITY AND TRACEABILITY
    // ========================================================
    AddedFinancialEntity =
        Table.AddColumn(
            UnpivotedProfiles,
            "Financial_Entity",
            each FinancialEntityKey,
            type text
        ),

    AddedSourceFile =
        Table.AddColumn(
            AddedFinancialEntity,
            "SourceFileName",
            each SourceFileName,
            type text
        ),

    AddedManualFeedFlag =
        Table.AddColumn(
            AddedSourceFile,
            "MainPlan_Option",
            each "Z",
            type text
        ),

    // ========================================================
    // APPLY FINAL DATA TYPES
    // ========================================================
    ChangedTypes =
        Table.TransformColumnTypes(
            AddedManualFeedFlag,
            {
                {"Account_Planning", type text},
                {"Calendar_Year", type text},
                {"Common_Key_Figure", type number},
                {"Financial_Entity", type text},
                {"SourceFileName", type text},
                {"MainPlan_Option", type text}
            }
        ),

    // ========================================================
    // FINAL COLUMN ORDER
    // ========================================================
    ReorderedColumns =
        Table.ReorderColumns(
            ChangedTypes,
            {
                "Financial_Entity",
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "SourceFileName",
                "MainPlan_Option"
            }
        )
in
    ReorderedColumns

// ========================================================
// ## ManualProfiles
// ========================================================

// This query is used to extract the manual feed profiles from the controlled manual feed files
//
// It works by performing the following steps:
// 1/ Retrieves the list of manual feed files from the ManualFeedFiles query
// 2/ Invokes the fnExtractManualProfiles function for every workbook in the list
// 3/ Appends all the extracted profile tables into a single table
// 4/ Applies the final data types and column order
// 5/ Returns the final table of manual feed profiles

let
    // ========================================================
    // CONTROLLED MANUAL WORKBOOK REGISTER
    // ========================================================
    Source =
        ManualFeedFiles,

    // ========================================================
    // INVOKE PROFILE FUNCTION FOR EVERY WORKBOOK
    // ========================================================
    ExtractedProfiles =
        Table.AddColumn(
            Source,
            "ManualProfiles",
            each
                fnExtractManualProfiles(
                    [Content],
                    [FinancialEntityKey],
                    [SourceFileName]
                ),
            type table
        ),

    // ========================================================
    // APPEND ALL WORKBOOK PROFILE TABLES
    // ========================================================
    CombinedProfiles =
        if Table.RowCount(ExtractedProfiles) = 0
        then
            #table(
                type table
                [
                    Financial_Entity = nullable text,
                    Account_Planning = nullable text,
                    Calendar_Year = nullable text,
                    Common_Key_Figure = nullable number,
                    SourceFileName = nullable text,
                    MainPlan_Option = nullable text
                ],
                {}
            )
        else
            Table.Combine(
                ExtractedProfiles[ManualProfiles]
            ),

    // ========================================================
    // FINAL DATA TYPES
    // ========================================================
    ChangedTypes =
        Table.TransformColumnTypes(
            CombinedProfiles,
            {
                {"Financial_Entity", type text},
                {"Account_Planning", type text},
                {"Calendar_Year", type text},
                {"Common_Key_Figure", type number},
                {"SourceFileName", type text},
                {"MainPlan_Option", type text}
            }
        ),

    // ========================================================
    // FINAL COLUMN ORDER
    // ========================================================
    ReorderedColumns =
        Table.ReorderColumns(
            ChangedTypes,
            {
                "Financial_Entity",
                "Account_Planning",
                "Calendar_Year",
                "Common_Key_Figure",
                "SourceFileName",
                "MainPlan_Option"
            },
            MissingField.Ignore
        )
in
    ReorderedColumns

// ========================================================
// ## fnExtractManualMetadata
// ========================================================

// This function is used to extract the manual feed metadata from the input template in the manual feed files

// It works by performing the following steps:
// 1/ Opens the workbook and retrieves the values of the defined names in the workbook
// 2/ Returns a single row table containing the extracted metadata values, along with the FinancialEntityKey and SourceFileName for traceability, and a manual feed flag column for traceability (ManualFeedFlag = "Y")
// 3/ Returns the final table of manual feed metadata

(
    FileContent as binary,
    FinancialEntityKey as number,
    SourceFileName as text
)
as table =>

let
    // ========================================================
    // OPEN THE EXCEL WORKBOOK
    // ========================================================
    WorkbookContents =
        Excel.Workbook(
            FileContent,
            null,
            true
        ),

    // ========================================================
    // HELPER FUNCTION:
    // RETURN THE FIRST VALUE FROM A SPECIFIED DEFINED NAME
    // ========================================================
    GetNamedRangeValue =
        (RangeName as text) as any =>

        let
            MatchingRange =
                Table.SelectRows(
                    WorkbookContents,
                    each
                        [Kind] = "DefinedName"
                        and [Name] = RangeName
                ),

            RangeTable =
                if Table.RowCount(MatchingRange) = 1
                then MatchingRange{0}[Data]
                else null,

            FirstColumnName =
                if RangeTable <> null
                    and Table.ColumnCount(RangeTable) > 0
                then Table.ColumnNames(RangeTable){0}
                else null,

            RangeValue =
                if RangeTable <> null
                    and Table.RowCount(RangeTable) > 0
                    and FirstColumnName <> null
                then Record.Field(
                    RangeTable{0},
                    FirstColumnName
                )
                else null
        in
            RangeValue,

    // ========================================================
    // EXTRACT THE REQUIRED WORKBOOK METADATA
    // ========================================================
    CaseName =
        GetNamedRangeValue("Case_Name"),
    
    CaseDescription =
        GetNamedRangeValue("Case_Description"),

    SegmentName =
        GetNamedRangeValue("Segment_Name"),

    EntityName =
        GetNamedRangeValue("Group_Entity_Name"),

    RegionName =
        GetNamedRangeValue("Region_Name"),

    CountryName =
        GetNamedRangeValue("Country_Name"),

    SegmentKey =
        GetNamedRangeValue("Segment_Key"),

    EntityKey =
        GetNamedRangeValue("Group_Entity_Key"),

    RegionKey =
        GetNamedRangeValue("Region_Key"),

    CountryKey =
        GetNamedRangeValue("Country_Key"),

    PlanTypeName =
        GetNamedRangeValue("Plan_Type_Name"),

    // ========================================================
    // RETURN ONE FINANCIAL ENTITY ROW FOR THIS WORKBOOK
    // ========================================================
    MetadataRow =
        #table(
            type table
            [
                FinancialEntityKey = nullable text,
                CaseName = nullable text,
                CaseDescription = nullable text,
                SegmentName = nullable text,
                EntityName = nullable text,                
                RegionName = nullable text,
                CountryName = nullable text,
                SegmentKey = nullable text,
                EntityKey = nullable text,                
                RegionKey = nullable text,
                CountryKey = nullable text,
                PlanTypeName = nullable text,
                SourceFileName = text,
                ManualFeedFlag = text
            ],
            {
                {
                    if FinancialEntityKey = null then null else Text.From(FinancialEntityKey),
                    if CaseName = null then null else Text.From(CaseName),
                    if CaseDescription = null then null else Text.From(CaseDescription),
                    if SegmentName = null then null else Text.From(SegmentName),
                    if EntityName = null then null else Text.From(EntityName),
                    if RegionName = null then null else Text.From(RegionName),
                    if CountryName = null then null else Text.From(CountryName),
                    if SegmentKey = null then null else Text.From(SegmentKey),
                    if EntityKey = null then null else Text.From(EntityKey),
                    if RegionKey = null then null else Text.From(RegionKey),
                    if CountryKey = null then null else Text.From(CountryKey),
                    if PlanTypeName = null then null else Text.From(PlanTypeName),
                    SourceFileName,
                    "Y"
                }
            }
        )
in
    MetadataRow

// ========================================================
// ## ManualMetaData
// ========================================================

// This query is used to consolidate the metadata extracted from the controlled manual feed files
// and align it to the Financial Entity dimension structure.
//
// It works by performing the following steps:
// 1/ Retrieves the controlled workbook register from the ManualFeedFiles query
// 2/ Invokes the fnExtractManualMetadata function for every workbook in the register
// 3/ Appends the extracted metadata rows into a single table
// 4/ Returns an empty table with the expected schema when no manual feed files are available
// 5/ Applies consistent data types to the combined metadata
// 6/ Renames the extracted fields to align with the Financial Entity dimension schema
// 7/ Adds an index to support downstream processing
// 8/ Returns the final manual Financial Entity metadata table

let
    // ========================================================
    // CONTROLLED MANUAL WORKBOOK REGISTER
    // ========================================================
    Source =
        ManualFeedFiles,

    // ========================================================
    // INVOKE METADATA FUNCTION FOR EVERY WORKBOOK
    // ========================================================
    ExtractedMetadata =
        Table.AddColumn(
            Source,
            "ManualMetadata",
            each
                fnExtractManualMetadata(
                    [Content],
                    [FinancialEntityKey],
                    [SourceFileName]
                ),
            type table
        ),

    // ========================================================
    // APPEND ALL WORKBOOK METADATA ROWS
    // ========================================================
    CombinedMetadata =
        if Table.RowCount(ExtractedMetadata) = 0
        then
            #table(
                type table
                [
                    FinancialEntityKey = nullable text,
                    CaseName = nullable text,
                    SegmentName = nullable text,
                    EntityName = nullable text,
                    RegionName = nullable text,
                    CountryName = nullable text,
                    SegmentKey = nullable text,
                    EntityKey = nullable text,
                    RegionKey = nullable text,
                    CountryKey = nullable text,
                    PlanTypeName = nullable text,
                    SourceFileName = nullable text,
                    ManualFeedFlag = nullable text
                ],
                {}
            )
        else
            Table.Combine(
                ExtractedMetadata[ManualMetadata]
            ),

    // ========================================================
    // FINAL DATA TYPES
    // ========================================================
    TypedMetadata =
        Table.TransformColumnTypes(
            CombinedMetadata,
            {
                {"FinancialEntityKey", type text},
                {"CaseName", type text},
                {"SegmentName", type text},
                {"EntityName", type text},
                {"RegionName", type text},
                {"CountryName", type text},
                {"SegmentKey", type text},
                {"EntityKey", type text},
                {"RegionKey", type text},
                {"CountryKey", type text},
                {"PlanTypeName", type text},
                {"SourceFileName", type text},
                {"ManualFeedFlag", type text}
            }
        ),

    // ========================================================
    // ALIGN TO FINANCIAL ENTITY DIMENSION SCHEMA
    // ========================================================
    RenamedColumns =
        Table.RenameColumns(
            TypedMetadata,
            {
                {"FinancialEntityKey", "Financial_Entity"},
                {"CaseName", "Financial_Entity_Text"},
                {"SegmentName", "Segment_Text"},
                {"EntityName", "BP_Group_Entities_Text"},
                {"RegionName", "Region_Text"},
                {"CountryName", "Country_Text"},
                {"SegmentKey", "Segment"},
                {"EntityKey", "BP_Group_Entities"},
                {"RegionKey", "Region"},
                {"CountryKey", "Country"},
                {"PlanTypeName", "MainPlan_Option_Text"}
            },
            MissingField.Ignore
        ),
    #"Added Index" = Table.AddIndexColumn(RenamedColumns, "Index", 1, 1, Int64.Type)
in
    #"Added Index"