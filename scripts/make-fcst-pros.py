#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import sys
import context
import json
from pathlib import Path


from datetime import datetime
from utils.plot import *
from context import json_dir, data_dir, img_dir


startTime = datetime.now()

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

# case_study = "high_level"
# model = "gfs"
# int_dir = "20190516T00"

# case_study = "sparks_lake"
# model = "gfs"
# int_dir = "20210625T00"

import getdata

case_study = sys.argv[1]
model = case_attrs[case_study]["model"]
int_dir = getdata.int_dir
print(case_study)

plot_list = [
    "25kPa",
    "50kPa",
    "100-50kPa",
    "70kPa-RH",
    "wsp",
    "t2m",
    "r2",
    "tp",
    "cape",
]


# plot_list = ["85kPa"]
pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
)


# pathlist = pathlist[7:8]
# pathlist = pathlist[16:17]
for i in range(len(pathlist)):
    # print(path)
    # figTime = datetime.now()
    ds = open_data(pathlist, i, model, "all_vars")
    print(
        f"Making Figs for Valid Datetime: {np.datetime_as_string(ds.valid_time, unit='h')}"
    )
    int_time = (
        np.datetime_as_string(ds.time, unit="h").replace("-", "").replace("T", "Z")
    )
    save_dir = Path(str(img_dir) + f"/{case_study}/{model}/{int_time}/")
    save_dir.mkdir(parents=True, exist_ok=True)

    ###################### 25 kPa  ######################
    if "25kPa" in plot_list:
        plot_25kPa(ds, case_study, save_dir)

    ###################### 50 kPa  ######################
    if "50kPa" in plot_list:
        plot_50kPa(ds, case_study, save_dir)

    #################### 100-50 kPa  ######################
    if "100-50kPa" in plot_list:
        plot_100_50kPa(ds, case_study, save_dir)

    #################### 100-50 kPa  ######################
    if "70kPa-RH" in plot_list:
        plot_70kPa_RH(ds, case_study, save_dir)

    ###################### 50 kPa  ######################
    if "85kPa" in plot_list:
        plot_85kPa(ds, case_study, save_dir)

    #################### Wsp Wdir  ######################
    if "wsp" in plot_list:
        plot_wspwdir(ds, case_study, save_dir, "10m", roads=True)
        plot_wspwdir(ds, case_study, save_dir, "100m", roads=True)
        plot_wspwdir(ds, case_study, save_dir, "85kPa")

    ##################### 2m Temp ######################
    if "t2m" in plot_list:
        plot_t2m(ds, case_study, save_dir, roads=True)

    ##################### 2m RH ######################
    if "r2" in plot_list:
        plot_r2(ds, case_study, save_dir, roads=True)

    ##################### Precip ######################
    if "tp" in plot_list:
        plot_tp(ds, case_study, save_dir, roads=True)

    ##################### Precip ######################
    if "cape" in plot_list:
        plot_cape(ds, case_study, save_dir, roads=True)


print("Total Run Time: ", datetime.now() - startTime)
