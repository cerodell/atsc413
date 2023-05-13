import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path


import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import xarray as xr

# import metpy.calc as mpcalc
# from metpy.cbook import get_test_data
# from metpy.interpolate import cross_section

from datetime import datetime
from context import data_dir, img_dir, json_dir
from utils.plot import base_plot, open_data, config_data

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


case_study = "high_level"
model = "gfs"
int_dir = "20190517T00"


pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}/").glob(f"*.grib2")
)
save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)


ds = open_data(pathlist[:1], 0, model, "all_vars")

ds_cross = ds.sel(
    longitude=slice(230, 250), latitude=slice(58, 56), isobaricInhPa=slice(1000, 500)
).mean(dim="latitude")
ds_cross["longitude"] = ds_cross["longitude"] - 360
ds_cross["wsp"] = ((ds_cross["u"] ** 2 + ds_cross["v"] ** 2) ** 0.5) * 3.6
# ds_cross['gh'] = ds_cross['gh'] - ds_cross['gh'].sel(isobaricInhPa= 1000)
# %%
var = "wsp"

levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "wxbell", colors, N=len(levels)
)


def setBold(txt):
    return r"$\bf{" + str(txt) + "}$"


vtimes, itime, stime = (
    pd.to_datetime(ds_cross.valid_time.values),
    pd.to_datetime(ds_cross.time.values),
    str(int(ds_cross.step.values.astype(float) / 3.6e12)),
)


fig = plt.figure(figsize=(14, 6))

ax = fig.add_subplot(1, 1, 1)

cs = ax.contour(
    ds_cross.longitude,
    ds_cross.isobaricInhPa,
    ds_cross["t"],
    colors="k",
    linewidths=1.0,
    linestyles="solid",
)
cb = plt.clabel(
    cs,
    fontsize=7,
    inline=1,
    inline_spacing=10,
    fmt="%i",
    rightside_up=True,
    use_clabeltext=True,
    zorder=10,
)

cf = ax.contourf(
    ds_cross.longitude,
    ds_cross.isobaricInhPa,
    ds_cross["wsp"],
    levels=levels,
    cmap=cmap,
)

ax.set_ylim(ax.get_ylim()[::-1])

cbar = plt.colorbar(cf, ax=ax, pad=0.04)
cbar.ax.tick_params(labelsize=10)
cbar.set_label(
    "Wind Speed \n" + r"($\mathrm{~m} \mathrm{~s}^{-1}$)",
    rotation=90,
    fontsize=10,
    labelpad=15,
)

ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
ax.set_title(
    f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
    loc="right",
)
plt.figtext(
    0.12,
    0.97,
    setBold("GFS") + " " + setBold("0.25") + r"$^o$ " + var_attrs[var]["title"],
    fontsize=14,
)

# %%
