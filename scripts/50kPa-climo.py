import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import xarray as xr


from datetime import datetime
from context import data_dir, img_dir, json_dir
from utils.plot import base_plot, open_data, config_data
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


case_study = "marshall_fire"
model = "gfs"
int_time = "20211231T00"


pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_time}/").glob(f"*.grib2")
)


longitude = slice(169, 351)
latitude = slice(90, 0)
ds = open_data(pathlist, 1, model, "all_vars")

# %%
ds_climo = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")
ds_t = ds_climo.salem.transform(ds["gh"].sel(isobaricInhPa=500))
ds_t = ds_t.sel(longitude=longitude, latitude=latitude)
ds_climo = ds_climo.sel(longitude=longitude, latitude=latitude)
vtimes = pd.to_datetime(ds.valid_time.values)
ds_climoold = ds_climo.sel(month=vtimes.month, hour=vtimes.hour)

day = vtimes.day
if day < 15:
    month_delta = -1
else:
    month_delta = 1
ctime = pd.to_datetime(ds.valid_time.values) + pd.Timedelta(days=month_delta * 30)

ds_climo = ds_climo.sel(month=[vtimes.month, ctime.month], hour=vtimes.hour)["gh"]
ds_climo["month"] = np.array([0, 31])
ds_climo = ds_climo.interp(month=np.arange(0, 31, 1)).isel(month=day - 1)


# %%
