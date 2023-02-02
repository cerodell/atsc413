import sys
import context
import json
import sys, os
import requests
import numpy as np
import pandas as pd
from pathlib import Path

from context import data_dir, json_dir
from utils.rad import get_data

# #############################  INPUTS  ####################################
# total arguments
# print("Total arguments passed:", n)
case_study = sys.argv[1]
print(case_study)

# # ## choose case study
# case_study = "high_level"
# # ## choose forecast model
# # model = "gfs"
# # ## choose forecast hour
# # init = "00"  # Z (UTC) time
# # ## choose forecast frequency
# # freq = 3  # in hours
# # date_range = pd.date_range("2019-05-16", "2019-05-18", freq=f"{freq}H")
# ############################################################################

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

## choose forecast model
model = case_attrs[case_study]["model"]
## choose forecast hour
init = case_attrs[case_study]["init"]  # Z (UTC) time
## choose forecast frequency
freq = case_attrs[case_study]["freq"]  # in hours
date_range = pd.date_range(
    case_attrs[case_study]["doi"][0], case_attrs[case_study]["doi"][1], freq=f"{freq}H"
)
make_dir = Path(str(data_dir) + f"/{model}/{case_study}")
make_dir.mkdir(parents=True, exist_ok=True)


int_fct = date_range[0]
fct_hours = np.arange(0, len(date_range) * freq, freq, dtype=int)

if model == "gfs":
    filelist = [
        f'/data/ds084.1/{int_fct.strftime("%Y")}/{int_fct.strftime("%Y%m%d")}/gfs.0p25.{int_fct.strftime("%Y%m%d")}{init}.f{str(fct_hour).zfill(3)}.grib2'
        for fct_hour in fct_hours
    ]
else:
    raise ValueError(f"{model} is an invalid model option at this time")


res = [
    os.path.isfile(str(make_dir) + "/" + file.rsplit("/", 1)[-1])
    for file in filelist
    if os.path.isfile(str(make_dir) + "/" + file.rsplit("/", 1)[-1]) != True
]


def check_item(file):
    return os.path.isfile(str(make_dir) + "/" + file.rsplit("/", 1)[-1])


filelist = list(filter(lambda file: check_item(file) != True, filelist))

if len(filelist) == 0:
    print(f"files for {case_study} previously downloaded")
else:
    get_data(filelist, make_dir)
