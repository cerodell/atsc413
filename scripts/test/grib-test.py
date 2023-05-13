import sys
import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from context import data_dir, img_dir, json_dir

model = "gfs"
case_study = "high_level"
int_dir = "20190517T00"

pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}/").glob(f"*.grib2")
)


# Import data
grib_data = cfgrib.open_datasets(pathlist[3])
# grib_data1 = cfgrib.open_datasets(pathlist[4])[26]

for i in range(len(grib_data)):
    print("============================================")
    print(i)
    # print(list(grib_data[i]))
    for var in grib_data[i]:
        print("-------------------------------------")
        print(f"{var}:  {grib_data[i][var].attrs['GRIB_name']}")
