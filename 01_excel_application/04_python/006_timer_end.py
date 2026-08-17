## This code block captures the end time of the model run and calculates the duration of the run.
# It formats the end time for display in the model log and computes the total run duration in seconds, providing users with information about how long the model took to execute. The results are returned to the user via the model log on the application home page, providing both business and technical details for users to understand the execution performance.

from datetime import datetime
from zoneinfo import ZoneInfo

try:
    run_end_model = datetime.now(ZoneInfo("Europe/London"))
    out = run_end_model.strftime("Last run:\n%d %b %y %H:%M:%S")
except Exception:
    out = "❌ Runtime error\nCheck logs"

out = run_end_model.strftime("Last run: %d %b %y %H:%M:%S")


run_duration = (
    f"⏱️ Run duration: "
    f"{(run_end_model - run_start_model).total_seconds():.2f} seconds"
)