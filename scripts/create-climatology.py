#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.compressor import compressor

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


## Earth's gravitational acceleration
g = 9.80665
data_dir = "/Volumes/WFRT-Data02/era5/"
var = "precip"
# pathlist = sorted(Path(data_dir).glob(f"era5-50kPa-monthly*"))
# open = datetime.now()
# ds = xr.open_mfdataset(pathlist, parallel=True)
# print("Opening Time: ", datetime.now() - open)

path = str(data_dir) + f"/era5-{var}-monthly-1991-2021.nc"
open = datetime.now()
ds = xr.open_dataset(path)
print("Opening Time: ", datetime.now() - open)


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds


def hour_mean(x):
    """
    function groups time to hourly and solves hourly mean

    """
    return x.groupby("time.hour").mean("time")


## group data into month day hour and solve the hourly means
# group = datetime.now()
# ds = ds.groupby("time.month").apply(hour_mean)
# ds = xr.apply_ufunc(hour_mean, ds, dask='parallelized',output_dtypes=[float], vectorize=True,)
# print("Grouping Time: ", datetime.now() - group)


# ## group data into month day hour and solve the hourly means
group = datetime.now()
ds = ds.groupby("time.month").apply(hour_mean)
print("Grouping Time: ", datetime.now() - group)


# loadTime = datetime.now()
# ds = ds.load()
# print("Loading Time: ", datetime.now() - loadTime)

ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs[
    "description"
] = "30 year (1991-2021) monthly averaged reanalysis by hour of day"

# ds, encoding = compressor(ds)

write = datetime.now()
ds.to_netcdf(
    str(data_dir) + f"/{var}-climatology.nc",
    mode="w",
    # encoding = encoding
)
print("Write Time: ", datetime.now() - write)


# open = datetime.now()
# ds = xr.concat([xr.open_dataset(path, chunks="auto") for path in pathlist],dim = 'time')
# print("Opening Time: ", datetime.now() - open)


# rechunk_time = datetime.now()
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)


# def hour_mean(x):
#     """
#     function groups time to hourly and solves hourly mean

#     """
#     return x.groupby('time.hour').mean('time')

# def day_mean(x):
#     """
#     function groups time to daily and feeds into hourly_mean

#     """
#     x = x.groupby('time.day').mean('time') #.apply(hour_mean)
#     # rechunk_time = datetime.now()
#     # x = rechunk(x)
#     # print("Rechunk Time: ", datetime.now() - rechunk_time)
#     return x
