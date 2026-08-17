## This code block defines a VBA subroutine that activates the scenario engine in an Excel workbook.
## It prompts the user for confirmation before proceeding with the activation, checks that the Python runtime is connected, and updates the status bar during the process.
## If an error occurs during the activation, it displays an error message with details about the issue
## The subroutine is designed to be used in an Excel application where the scenario engine is triggered via Python calculations, and it provides feedback to the user throughout the process.
## The subroutine is intended to be run from a button on the Home sheet of the workbook, and it assumes that the user has the necessary permissions to run Python calculations.
## The key step is Excel's calculation mode. By default, Excel is set to semi-automatic calculation mode (partial),this
## This prevents Excel normal inputs and calculations perpetually re-triggering the Python code.
## The code changes the calculation mode to automatic, adds in a small Python code equivalent to a print of a text string, and then triggers the rest of the Python code to execute.
## Note Excel executes Python code in top to bottom, left to right per sheet and then works from leftmost sheet to rightmost sheet.
## The code is designed to be run from the Home sheet, which is the leftmost sheet in the workbook.

Option Explicit

Public Sub ActivateMe()

    Dim response As VbMsgBoxResult

    response = MsgBox( _
        "Run the scenario engine?", _
        vbYesNo + vbQuestion + vbDefaultButton2, _
        "Run Scenario Engine")

    If response <> vbYes Then Exit Sub

    response = MsgBox( _
        "Before continuing, confirm that the Python runtime is connected." & vbCrLf & vbCrLf & _
        "If any Python cells display #CONNECT! or #BLOCKED!, select Reset Runtime " & _
        "from the Python controls in the Formulas ribbon and wait for the workbook to reconnect." & vbCrLf & vbCrLf & _
        "Continue with the scenario engine run?", _
        vbYesNo + vbExclamation + vbDefaultButton2, _
        "Confirm Python Runtime")

    If response <> vbYes Then Exit Sub

    On Error GoTo RunError

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.StatusBar = "Starting the scenario engine..."

    Application.Calculation = xlCalculationAutomatic

    Range("A1").Formula2R1C1 = _
        "=PY(""""""Activate me"""""",1)"

    Application.Calculation = xlCalculationSemiautomatic

    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True

    MsgBox _
        "The scenario engine has been triggered." & vbCrLf & vbCrLf & _
        "Allow the Python calculations to complete before refreshing outputs.", _
        vbInformation, _
        "Scenario Engine Started"

    Exit Sub

RunError:

    Application.Calculation = xlCalculationSemiautomatic
    Application.StatusBar = False
    Application.EnableEvents = True
    Application.ScreenUpdating = True

    MsgBox _
        "The scenario engine could not be started." & vbCrLf & vbCrLf & _
        Err.Description & vbCrLf & vbCrLf & _
        "If Python cells display #CONNECT! or #BLOCKED!, reset the Python runtime and try again.", _
        vbExclamation, _
        "Scenario Engine Error"

End Sub

