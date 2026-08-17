## This code block defines a VBA subroutine that refreshes the scenario reporting outputs in an Excel workbook.
## It prompts the user for confirmation before proceeding with the refresh, updates the status bar during the process, and writes a timestamp to a specified cell upon successful completion.
## If an error occurs during the refresh, it displays an error message with details about the issue.    
## The subroutine is designed to be used in an Excel application where scenario results are generated and displayed, and it provides feedback to the user throughout the process.
## The subroutine is intended to be run from a button on the Home sheet of the workbook, and it assumes that the user has the necessary permissions to refresh the scenario results.
## Note this code assumes that refreshing Excel's datamodel will subsequently trigger the refresh of all dependent reporting outputs, including pivot tables and charts, which are linked to the scenario results dataset.

Option Explicit

Public Sub RefreshScenarioOutputs()

    Dim wsHome As Worksheet
    Dim response As VbMsgBoxResult

    Set wsHome = ThisWorkbook.Worksheets("Home")

    response = MsgBox( _
        "Refresh the scenario reporting outputs?", _
        vbYesNo + vbQuestion + vbDefaultButton2, _
        "Refresh Outputs")

    If response <> vbYes Then Exit Sub

    response = MsgBox( _
        "Are you sure?" & vbCrLf & vbCrLf & _
        "This will refresh the Scenario Results dataset and reporting outputs.", _
        vbYesNo + vbExclamation + vbDefaultButton2, _
        "Confirm Refresh")

    If response <> vbYes Then Exit Sub

    On Error GoTo RefreshError

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.StatusBar = _
        "Refreshing scenario reporting outputs..."


    ' ========================================================
    ' 1. REFRESH SCENARIO RESULTS CONNECTION
    ' ========================================================

    ThisWorkbook.Connections( _
        "Query - ScenarioResults" _
    ).Refresh

    Application.CalculateUntilAsyncQueriesDone


    ' ========================================================
    ' 2. UPDATE REFRESH TIMESTAMP
    ' ========================================================

    With wsHome.Range("A4")
        .Value = _
            "Last refreshed: " & _
            Format(Now, "dd mmm yy hh:mm:ss")
    End With


    ' ========================================================
    ' 3. RESTORE APPLICATION STATE
    ' ========================================================

    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True


    ' ========================================================
    ' 4. FINAL MESSAGE
    ' ========================================================

    MsgBox _
        "Scenario reporting outputs refreshed successfully.", _
        vbInformation, _
        "Refresh Complete"

    Exit Sub


RefreshError:

    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True

    MsgBox _
        "The reporting outputs could not be refreshed." & _
        vbCrLf & vbCrLf & _
        Err.Description, _
        vbExclamation, _
        "Refresh Failed"

End Sub