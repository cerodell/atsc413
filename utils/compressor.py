import context
import os
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


# def compressor(ds):
#     """
#     this function compresses datasets
#     """
#     ds = ds.load()
#     comp = dict(zlib=True, complevel=9)
#     encoding = {var: comp for var in ds.data_vars}
#     for var in ds.data_vars:
#         ds[var].attrs = var_dict[var]

#     return ds, encoding
