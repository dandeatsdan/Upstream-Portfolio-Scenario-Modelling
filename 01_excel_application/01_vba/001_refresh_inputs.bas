## This code block defines a VBA subroutine that refreshes the source input data connections in an Excel workbook.
## It prompts the user for confirmation before proceeding with the refresh, updates the status bar during the process, and writes a timestamp to a specified cell upon successful completion.
## If an error occurs during the refresh, it displays an error message with details about the failed connection.
## The subroutine is designed to be used in an Excel application where multiple data connections need to be refreshed, and it provides feedback to the user throughout the process.
## Note that the connections are to a Power BI semantic model, and data is retrievd using OLE DB connections and DAX expressions.
## The subroutine is intended to be run from a button on the Home sheet of the workbook, and it assumes that the user has the necessary permissions to refresh the data connections.
## Data access is verified by the Power BI service working in conjunction with Microsoft Entra ID, and the user must be signed in to their Power BI account to successfully refresh the data.

Option Explicit

Public Sub RefreshInputs()

    Dim response As VbMsgBoxResult
    Dim ws As Worksheet
    Dim connectionNames As Variant
    Dim connectionName As Variant

    'Change this to the sheet and cell used for the input timestamp
    Set ws = ThisWorkbook.Worksheets("Home")

    connectionNames = Array( _
        "OGLTPDataPipeline_CaseListing", _
        "OGLTPDataPipeline_Profiles", _
        "OGLTPDataPipeline_TotalsAvgs" _
    )

    'First confirmation
    response = MsgBox( _
        "Refresh the source input data?", _
        vbYesNo + vbQuestion + vbDefaultButton2, _
        "Refresh Inputs")

    If response <> vbYes Then Exit Sub

    'Second confirmation
    response = MsgBox( _
        "Are you sure?" & vbCrLf & vbCrLf & _
        "This will refresh the case listing, profile data and supporting totals and averages.", _
        vbYesNo + vbExclamation + vbDefaultButton2, _
        "Confirm Input Refresh")

    If response <> vbYes Then Exit Sub

    On Error GoTo RefreshError

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.StatusBar = "Refreshing source input data..."

    'Refresh each source-data connection
    For Each connectionName In connectionNames

        Application.StatusBar = _
            "Refreshing " & CStr(connectionName) & "..."

        ThisWorkbook.Connections(CStr(connectionName)).Refresh

    Next connectionName

    'Wait for Power Query refreshes to finish
    Application.CalculateUntilAsyncQueriesDone

    'Write the timestamp
    With ws.Range("A3")
        .Value = "Last refreshed: " & _
                 Format(Now, "dd mmm yy hh:mm:ss")

    End With

    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True

    MsgBox _
        "Source input data refreshed successfully.", _
        vbInformation, _
        "Input Refresh Complete"

    Exit Sub

RefreshError:

    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True

    MsgBox _
        "The source input data could not be refreshed." & vbCrLf & vbCrLf & _
        "Connection: " & CStr(connectionName) & vbCrLf & _
        "Error: " & Err.Description, _
        vbExclamation, _
        "Input Refresh Failed"

End Sub