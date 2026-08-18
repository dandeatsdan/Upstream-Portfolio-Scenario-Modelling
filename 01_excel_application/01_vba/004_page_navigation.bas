' This code block defines a set of VBA subroutines for navigating between different worksheets (pages) in an Excel workbook.
' Each subroutine corresponds to a specific worksheet and uses a helper function to open the desired page.
' The subroutines provide a user-friendly way to switch between the Home page, various scenario pages, the health stats page, results page, dashboard, and help page.
' The OpenPage function handles the actual navigation, ensuring that the target worksheet is made visible and activated.
' The subroutines are designed to be triggered by buttons or other controls on the Home sheet, allowing users to easily access different parts of the application without manually searching for the worksheets.
' The ShowTechSheets and HideTechSheets subroutines allow users to toggle the visibility of technical worksheets, providing a way to access or hide detailed data and configuration sheets as needed.

Option Explicit


Private Sub OpenPage(ByVal sheetName As String)

    Dim ws As Worksheet

    On Error GoTo NavigationError

    Application.ScreenUpdating = False

    Set ws = ThisWorkbook.Worksheets(sheetName)

    'Make the worksheet visible if it is hidden
    ws.Visible = xlSheetVisible

    'Open the worksheet
    ws.Activate

CleanExit:
    Application.ScreenUpdating = True
    Exit Sub

NavigationError:
    Application.ScreenUpdating = True

    MsgBox _
        "The page could not be opened." & vbCrLf & vbCrLf & _
        "Worksheet: " & sheetName & vbCrLf & vbCrLf & _
        "Please check that the worksheet name is correct.", _
        vbExclamation, _
        "Navigation Error"

End Sub


Public Sub GoToHome()
    OpenPage "Home"
End Sub


Public Sub GoToScenario1()
    OpenPage "Scenario 1"
End Sub


Public Sub GoToScenario2()
    OpenPage "Scenario 2"
End Sub


Public Sub GoToScenario3()
    OpenPage "Scenario 3"
End Sub


Public Sub GoToScenario4()
    OpenPage "Scenario 4"
End Sub


Public Sub GoToScenario5()
    OpenPage "Scenario 5"
End Sub


Public Sub GoToHealth()
    OpenPage "Scenario Health Stats"
End Sub


Public Sub GoToResults()
    OpenPage "Results"
End Sub


Public Sub GoToDashboard()
    OpenPage "Dashboard"
End Sub


Public Sub GoToHelp()
    OpenPage "Help"
End Sub


Sub ShowTechSheets()

    Application.ScreenUpdating = False
    Sheets("Home").Select
    Sheets("Scenario Health Stats").Visible = -1
    Sheets("Timer Start").Visible = -1
    Sheets("Cases and Rates").Visible = -1
    Sheets("Profiles").Visible = -1
    Sheets("Scenario Config").Visible = -1
    Sheets("Operations Library").Visible = -1
    Sheets("Engine Output").Visible = -1
    Sheets("Model Log").Visible = -1
    Sheets("Timer End").Visible = -1
    Sheets("Home").Select
    
End Sub

Sub HideTechSheets()

    Application.ScreenUpdating = False
    Sheets("Home").Select
    Sheets("Scenario Health Stats").Visible = 2
    Sheets("Timer Start").Visible = 2
    Sheets("Cases and Rates").Visible = 2
    Sheets("Profiles").Visible = 2
    Sheets("Scenario Config").Visible = 2
    Sheets("Operations Library").Visible = 2
    Sheets("Engine Output").Visible = 2
    Sheets("Model Log").Visible = 2
    Sheets("Timer End").Visible = 2
    Sheets("Home").Select
    
End Sub
