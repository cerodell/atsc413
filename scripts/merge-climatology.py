#!/Users/crodell/miniconda3/envs/atsc413/bin/python
import context
import time
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
from dask.distributed import Client

from utils.compressor import compressor


# client = Client(n_workers=2, threads_per_worker=2, memory_limit='1GB')

## Earth's gravitational acceleration
g = 9.80665
data_dir = "/Volumes/WFRT-Data02/era5/"

varlist = ["50kPa", "temp", "mslp", "precip"]

open = datetime.now()
ds = xr.merge(
    [xr.open_dataset(str(data_dir) + f"/{var}-climatology.nc") for var in varlist]
)
print("Opening Time: ", datetime.now() - open)


ds["gh"] = ds["z"] / g
ds["gh"].attrs["units"] = "m"
ds = ds.drop(["z"])

ds, encoding = compressor(ds)
ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs[
    "description"
] = "30 year (1991-2021) monthly averaged reanalysis by hour of day"
for var in ds:
    ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"


write = datetime.now()
ds.to_netcdf(str(data_dir) + f"/climatology-1991-2021.nc", mode="w", encoding=encoding)
print("Write Time: ", datetime.now() - write)
