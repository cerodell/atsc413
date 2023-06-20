#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import json
import os
import sys
import time
import pandas as pd
from pathlib import Path

from context import json_dir, root_dir
from datetime import datetime, date, timedelta
import cartopy

cartopy.__version__

startTime = datetime.now()


print(os.path.expanduser("~"))
case_study = "kimiwan_complex"

## download historical forecast data
command = f"{os.path.expanduser('~')}//miniconda3/envs/atsc413/bin/python {root_dir}/scripts/getdata.py {case_study}"
os.system(command)


# ## create forecast products from historical forecast data
command = f"{os.path.expanduser('~')}//miniconda3/envs/atsc413/bin/python {root_dir}/scripts/make-fcst-pros.py {case_study}"
os.system(command)
