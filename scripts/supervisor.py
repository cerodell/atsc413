import context
import json
import os
import sys
import time
import pandas as pd
from pathlib import Path

from context import json_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()


with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)
