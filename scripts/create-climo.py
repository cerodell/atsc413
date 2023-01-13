#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcdf-file


## Earth's gravitational acceleration
g = 9.80665
data_dir = "/Volumes/WFRT-Data02/era5"

ds = xr.open_dataset(data_dir + "/era5-50kPa-2010-2021.nc", chunks="auto")


ds = ds.sel(time="2012-01-01T00")
kPa = ds.z / 9.80665

# define a function with the hourly calculation:
def hour_mean(x):
    return x.groupby("time.hour").mean("time")


# group by month, then apply the function:
ds1 = ds.groupby("time.month").apply(hour_mean)

kPa50 = ds1.isel(month=10, hour=20)

kPa50.z.plot()
