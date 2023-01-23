#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

# from utils.compressor import compressor

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


## Earth's gravitational acceleration
g = 9.80665
data_dir = "/Volumes/WFRT-Data02/era5/"

pathlist = sorted(Path(data_dir).glob(f"era5-50kPa-monthly*"))


open = datetime.now()
ds = xr.open_mfdataset(pathlist, parallel=True)
print("Opening Time: ", datetime.now() - open)


# ds = ds.sel(time = slice("1991-01-01","1993-01-01"))
# ds = ds.resample(time="1D").mean(dim = 'time'


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
group = datetime.now()
ds = ds.groupby("time.month").apply(hour_mean)
print("Grouping Time: ", datetime.now() - group)

ds = rechunk(ds)

# rechunk_time = datetime.now()
# final_ds = final_ds.isel(month= 0, day = 1)
# print(final_ds)
# final_ds = rechunk(final_ds)
# print("Rechunk Time: ", datetime.now() - rechunk_time)

print("Starting Compute Time: ", datetime.now())
compute = datetime.now()
final_ds = ds.compute()
print("Compute Time: ", datetime.now() - compute)


final_ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
final_ds.attrs[
    "description"
] = "Monthly averaged reanalysis by hour of day over 30 years (1991-2021)"


write = datetime.now()
final_ds.to_netcdf(
    str(data_dir) + f"/zz50kPa-Climo.nc",
    mode="w",
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
