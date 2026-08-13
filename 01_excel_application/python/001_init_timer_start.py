## Excel workbook application for Upstream Portfolio Scenario Modelling
## This script sets up the Python environment for the Excel application, including
## importing required libraries, setting up the Excel interface, and configuring the run timer.
## Note the specific commands used to set up the Excel interface and timer, which are essential for the application's functionality.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels as sm
import excel
import warnings
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

warnings.simplefilter('ignore')

excel.set_xl_scalar_conversion(excel.convert_to_scalar)
excel.set_xl_array_conversion(excel.convert_to_dataframe)


## Set the engine run timer
## Output the run start time to Excel for auditability and traceability
## Output in the format: Last run: 01 Jan 23 12:00:00 and per the zone Europe/London

run_start_model = datetime.now(ZoneInfo("Europe/London"))
out = run_start_model.strftime("Last run: %d %b %y %H:%M:%S")