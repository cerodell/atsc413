#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import json
import numpy as np
import pandas as pd
import xarray as xr
import cfgrib

from pathlib import Path


import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter
from cartopy.feature import NaturalEarthFeature

import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units
from metpy.plots import StationPlot

from metpy.cbook import get_test_data
from metpy.interpolate import cross_section

from datetime import datetime
from context import data_dir, img_dir, json_dir, root_dir
from utils.plot import base_plot, open_data, config_data, setBold
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


############################################################
## LOW LEVEL JET
# https://www.theweatherprediction.com/habyhints2/696/
############################################################
with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

case_study = "kimiwan_complex"
model = "gfs"
int_time = "20230516T00"


ds = xr.open_dataset(str(root_dir) + f"/data/hw/gfs.nc")
save_dir = Path(str(root_dir) + f"/img/hw/")
save_dir.mkdir(parents=True, exist_ok=True)

# %%
var = "50kPa"
figTime = datetime.now()
var_name = "gh"
ds, ds_climo, ds_t, extent, center = config_data(ds, var, case_study, anomaly=False)
ds = ds.sel(isobaricInhPa=500)
# %%
plotcrs = ccrs.PlateCarree()

lons, lats, vtimes, itime, stime = (
    ds.longitude.values,
    ds.latitude.values,
    pd.to_datetime(ds.valid_time.values),
    pd.to_datetime(ds.time.values),
    str(int(ds.step.values.astype(float) / 3.6e12)),
)
# Download and add the states and coastlines
states = NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_shp",
)
#############################################
# fig = plt.figure(1, figsize =(16,16))
# gs = gridspec.GridSpec(
#     2, 1, height_ratios=[1, 0.02], bottom=0.07, top=0.99, hspace=0.01, wspace=0.01
# )

# ax = plt.subplot(gs[0], projection=plotcrs)
# ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
# ax.set_title(
#     f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
#     loc="right",
# )
# plt.figtext(
#     0.13,
#     .78,
#     setBold("GFS") + " " + setBold("0.25") + r"$^o$ " + "50kPa Geopotential Heights (dam)",
#     fontsize=14,
# )

# ax.coastlines("50m", edgecolor="black", linewidth=0.1)
# ax.add_feature(states, linewidth=0.1, edgecolor="black")

# lons, lats = np.meshgrid(lons, lats)

# ax.coastlines("50m", edgecolor="grey", linewidth=0.1)
# ax.add_feature(cfeature.STATES, edgecolor="grey", linewidth=0.1)
# skip = 35

# # Set up station plotting using only every third
# # element from arrays for plotting
# stationplot = StationPlot(
#     ax,
#     lons[::skip, ::skip].ravel(),
#     lats[::skip, ::skip].ravel(),
#     transform=ccrs.PlateCarree(),
#     fontsize=18,
# )

# stationplot.plot_parameter(
#     (0, 1), ds[var_name].values[::skip, ::skip].ravel()/10, zorder=10, fontsize=8
# )
# ax.set_extent([-170, -30, 5, 85], ccrs.PlateCarree())
# plt.savefig(
#     str(save_dir) + f"/{var}-{var_name}-{vtimes.strftime('%Y%m%d%H')}.pdf",
#     bbox_inches="tight",
#     orientation='landscape'
# )
# plt.close()


##################################################################################################################
fig = plt.figure(1, figsize=(16, 16))
gs = gridspec.GridSpec(
    2, 1, height_ratios=[1, 0.02], bottom=0.07, top=0.99, hspace=0.01, wspace=0.01
)

ax = plt.subplot(gs[0], projection=plotcrs)
ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
ax.set_title(
    f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
    loc="right",
)
plt.figtext(
    0.13,
    0.78,
    setBold("GFS")
    + " "
    + setBold("0.25")
    + r"$^o$ "
    + "50kPa Geopotential Heights (dam)",
    fontsize=14,
)

ax.coastlines("50m", edgecolor="black", linewidth=0.1)
ax.add_feature(states, linewidth=0.1, edgecolor="black")
lons, lats = np.meshgrid(lons, lats)
ax.coastlines("50m", edgecolor="grey", linewidth=0.1)
ax.add_feature(cfeature.STATES, edgecolor="grey", linewidth=0.1)
skip = 35

cs = ax.contour(
    lons[::skip, ::skip],
    lats[::skip, ::skip],
    ds[var_name].values[::skip, ::skip] / 10,
    var_attrs[var]["levels"]["raw"],
    colors="k",
    linewidths=1.0,
    linestyles="solid",
    transform=ccrs.PlateCarree(),
)

# Set up station plotting using only every third
# element from arrays for plotting
stationplot = StationPlot(
    ax,
    lons[::skip, ::skip].ravel(),
    lats[::skip, ::skip].ravel(),
    transform=ccrs.PlateCarree(),
    fontsize=18,
)

stationplot.plot_parameter(
    (0, 1), ds[var_name].values[::skip, ::skip].ravel() / 10, zorder=10, fontsize=8
)
ax.set_extent([-170, -30, 5, 85], ccrs.PlateCarree())
# plt.show()
plt.savefig(
    str(save_dir) + f"/{var}-{var_name}-{vtimes.strftime('%Y%m%d%H')}-solution.pdf",
    bbox_inches="tight",
    orientation="landscape",
)
plt.close()
