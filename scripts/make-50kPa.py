import context
import numpy as np
import xarray as xr


from context import data_dir


ds_gfs = xr.open_dataset(
    str(data_dir) + f"/nam_218_20190516_0000_000.grb2", engine="cfgrib"
)


import cfgrib
import xarray as xr


# Import data
grib_data = cfgrib.open_datasets("\era5land_extract.grib")


# Merge both tp arrays into one on the time dimension
grib_precip = xr.merge([grib_data[1], grib_data[2]])
