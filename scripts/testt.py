import context
import xarray as xr


import pandas as pd

from context import data_dir


fct_day = pd.Timestamp("2025-01-06")
ds_era5 =  xr.open_dataset(f"{data_dir}/ecmwf/era5/{fct_day.strftime('%Y%m')}/era5-single-levels-{fct_day.strftime('%Y%m%d')}.grib")
    