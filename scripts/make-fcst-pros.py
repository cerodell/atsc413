#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import sys
import context
import json
import os.path
from pathlib import Path
import cfgrib

from datetime import datetime
from utils.plot import *
from context import json_dir, data_dir, img_dir
import getdata

case_study = sys.argv[1]
model = case_attrs[case_study]["model"]


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

# case_study = "kimiwan_complex"
# model = "gfs"
# int_dir = "20230522T00"


# case_study = "qb_fires"
# model = "gfs"

fct_days = pd.date_range(
    case_attrs[case_study]["fct_days"][0], case_attrs[case_study]["fct_days"][1]
)

# int_dir = getdata.int_dir
print(case_study)

plot_list = [
    "25kPa",
    "50kPa",
    "100-50kPa",
    "70kPa-RH",
    "wsp-10m",
    "wsp-100m",
    "wsp-85kPa",
    "t2m",
    "t2m-anomaly",
    "r2",
    "tp",
    "cape",
]

for fct_day in fct_days:
    int_dir = fct_day.strftime("%Y%m%dT%H")
    pathlist = sorted(
        Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
    )
    for i in range(len(pathlist)):
        # print(path)
        int_time = int_dir.replace("T", "Z")
        save_dir = Path(str(img_dir) + f"/{case_study}/{model}/{int_time}/")
        save_dir.mkdir(parents=True, exist_ok=True)
        fct = int(
            str(pathlist[i]).rsplit("/", 1)[1].rsplit(".", 1)[0].rsplit(".", 1)[1][1:]
        )
        vtimes = fct_day + pd.Timedelta(hours=fct)
        mask = np.array(
            [
                os.path.exists(
                    str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg"
                )
                for var in plot_list
            ]
        )
        if np.all(mask == True):
            pass
        else:
            plot_i = list(np.array(plot_list)[mask == False])
            ds = open_data(pathlist, i, model, "all_vars")
            try:
                ds["atp"] = ds["tp"] + ds_i["atp"]
            except:
                ds["atp"] = ds["t2m"] * 0
            print(
                f"Making Figs for Valid Datetime: {np.datetime_as_string(ds.valid_time, unit='h')} with Int time: {int_time}"
            )
            ###################### 25 kPa  ######################
            if "25kPa" in plot_i:
                plot_25kPa(ds, case_study, save_dir)

            ###################### 50 kPa  ######################
            if "50kPa" in plot_i:
                plot_50kPa(ds, case_study, save_dir)

            #################### 100-50 kPa  ######################
            if "100-50kPa" in plot_i:
                plot_100_50kPa(ds, case_study, save_dir)

            #################### 100-50 kPa  ######################
            if "70kPa-RH" in plot_i:
                plot_70kPa_RH(ds, case_study, save_dir)

            ###################### 50 kPa  ######################
            if "85kPa" in plot_i:
                plot_85kPa(ds, case_study, save_dir)

            #################### Wsp Wdir  ######################
            if "wsp-10m" in plot_i:
                plot_wspwdir(ds, case_study, save_dir, "10m", roads=True)

            #################### Wsp Wdir  ######################
            if "wsp-100m" in plot_i:
                plot_wspwdir(ds, case_study, save_dir, "100m", roads=True)

            #################### Wsp Wdir  ######################
            if "wsp-85kPa" in plot_i:
                plot_wspwdir(ds, case_study, save_dir, "85kPa")

            ##################### 2m Temp ######################
            if "t2m" in plot_i:
                plot_t2m(ds, case_study, save_dir, roads=True)

            ##################### 2m Temp ######################
            if "t2m-anomaly" in plot_i:
                plot_t2m_anomaly(ds, case_study, save_dir, roads=True)

            ##################### 2m RH ######################
            if "r2" in plot_i:
                plot_r2(ds, case_study, save_dir, roads=True)

            ##################### Precip ######################
            if "tp" in plot_i:
                plot_tp(ds, case_study, save_dir, roads=True)

            ##################### Precip ######################
            if "cape" in plot_i:
                plot_cape(ds, case_study, save_dir, roads=True)

            ds_i = ds
print("Total Run Time: ", datetime.now() - startTime)
