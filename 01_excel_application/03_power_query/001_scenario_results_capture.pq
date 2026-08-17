## This code block defines a Power Query M script that processes scenario results data from an Excel workbook.
## The script retrieves data from a named range "FromArray_2" in the current workbook - this is the special array named range for the Python dataframe output
## The simple script promotes the first row to headers, and changes the data types of specific columns to ensure proper formatting for further analysis.
## The processed data includes columns for Scenario, Scenario Name, ID, Case, Group Entity, Segment, Region, Country, Plan Type, Operation, Param1, Param2, Param3, Metric, Year, Value, and RunDateTime.
## The script is designed to be used in an Excel application where scenario results are captured and analyzed, providing a structured dataset for reporting and decision-making.
## Note that the data types are explicitly defined to ensure consistency and accuracy in downstream calculations and visualizations, and the script assumes that the named range "FromArray_2" exists and contains valid data.

let
    Source = Excel.CurrentWorkbook(){[Name="FromArray_2"]}[Content],
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Scenario", type text}, {"Scenario Name", type text}, {"ID", Int64.Type}, {"Case", type text}, {"Group Entity", type text}, {"Segment", type text}, {"Region", type text}, {"Country", type text}, {"Plan Type", type text}, {"Operation", type text}, {"Param1", Int64.Type}, {"Param2", Int64.Type}, {"Param3", Int64.Type}, {"Metric", type text}, {"Year", Int64.Type}, {"Value", type number}, {"RunDateTime", type datetime}})
in
    #"Changed Type"