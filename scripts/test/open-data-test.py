import sys
import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from context import json_dir, data_dir


with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


# def open_data(path, model, var, case_study, transform=False):

case_study = "high_level"
var = "all_vars"
model = "gfs"

pathlist = sorted(Path(str(data_dir) + f"/{model}/{case_study}/").glob(f"*.grib2"))
i = 0
# path = pathlist[1]

# if len(var_attrs[var]["domain"]) == 2:
#     plat, plon = var_attrs[var]["domain"][0], var_attrs[var]["domain"][1]
#     center = case_attrs[case_study]["loc"]
#     lat, lon = int(center[0]), int(center[1])
#     extent = [lon - plon, lon + plon, lat - plat, lat + plat]
#     longitude = slice(extent[0] + 360, extent[1] + 360)
#     latitude = slice(extent[-1], extent[-2])
# else:
#     extent = var_attrs[var]["domain"]
#     longitude = slice(169, 351)
#     latitude = slice(90, 0)

if (
    any(isinstance(i, dict) for i in var_attrs[var]["filter_by_keys"][model].values())
    == False
):
    ds = xr.open_dataset(
        pathlist[i],
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": var_attrs[var]["filter_by_keys"][model]},
    )
elif (
    any(isinstance(i, dict) for i in var_attrs[var]["filter_by_keys"][model].values())
    == True
):
    ds_list = []
    for filter_by_keys in var_attrs[var]["filter_by_keys"][model]:
        try:
            ds_i = xr.open_dataset(
                pathlist[i],
                engine="cfgrib",
                backend_kwargs={
                    "filter_by_keys": var_attrs[var]["filter_by_keys"][model][
                        filter_by_keys
                    ]
                },
            )
            if filter_by_keys == "tp":
                try:
                    ds_ii = xr.open_dataset(
                        pathlist[i - 1],
                        engine="cfgrib",
                        backend_kwargs={
                            "filter_by_keys": var_attrs[var]["filter_by_keys"][model][
                                filter_by_keys
                            ]
                        },
                    )
                    ds_i = ds_i - ds_ii
                except:
                    pass
            ds_list.append(ds_i)
            print(filter_by_keys)
        except:
            pass
    ds = xr.merge(ds_list, compat="override")
else:
    raise ValueError("Bad filter_by_key options")

# if transform == True:
#     ## ONLY WORKS FOR GH AT 50 kPa
#     ## TODO make this better et up for other climo variables
#     ds_climo = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")
#     ds_t = ds_climo.salem.transform(ds["gh"].sel(isobaricInhPa=500))
#     ds_t = ds_t.sel(longitude=longitude, latitude=latitude)
#     ds_climo = ds_climo.sel(longitude=longitude, latitude=latitude)
#     vtimes = pd.to_datetime(ds.valid_time.values)
#     ds_climo = ds_climo.sel(month=vtimes.month, hour=vtimes.hour)
# else:
#     ds_climo, ds_t = None, None

# ds = ds.sel(longitude=longitude, latitude=latitude)

# return ds, ds_climo, ds_t
