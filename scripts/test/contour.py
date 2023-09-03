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

pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_time}/").glob(f"*.grib2")
)
# ds = open_data(pathlist, 4, model, "upper")
# ds.to_netcdf(str(root_dir) + f"/data/hw/gfs.nc")


ds = xr.open_dataset(str(root_dir) + f"/data/hw/gfs.nc")

save_dir = Path(str(img_dir) + f'/{case_study}/{model}/{int_time.replace("T", "Z")}/')
save_dir.mkdir(parents=True, exist_ok=True)


# uwnd_500, vwnd_500 = ds['u_earth'].sel(isobaricInhPa = 500) * units('m/s'), ds['v_earth'].sel(isobaricInhPa = 500) * units('m/s')
# dx, dy = ds['longitude'], ds['latitude']
# # div_500 = mpcalc.divergence(uwnd_500, vwnd_500, dx=dx, dy=dy)

# div_500 = mpcalc.divergence(uwnd_500, vwnd_500)
# %%
var = "50kPa"
figTime = datetime.now()
var_name = "gh"
ds, ds_climo, ds_t, extent, center = config_data(ds, var, case_study, anomaly=False)
ds = ds.sel(isobaricInhPa=500)

plotcrs = ccrs.LambertConformal(
    central_longitude=-100.0, central_latitude=40.0, standard_parallels=[30, 60]
)
# plotcrs =  ccrs.NorthPolarStereo(central_longitude=-100.0)
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
fig = plt.figure(1, figsize=(14, 12))
gs = gridspec.GridSpec(
    2, 1, height_ratios=[1, 0.02], bottom=0.07, top=0.99, hspace=0.01, wspace=0.01
)

ax = plt.subplot(gs[0], projection=plotcrs)
ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
ax.set_title(
    f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
    loc="right",
)
# plt.figtext(
#     0.12,
#     1,
#     setBold("GFS") + " " + setBold("0.25") + r"$^o$ " + var_attrs[var]["title"],
#     fontsize=14,
# )

ax.coastlines("50m", edgecolor="black", linewidth=0.3)
ax.add_feature(states, linewidth=0.3, edgecolor="black")

lons, lats = np.meshgrid(lons, lats)

ax.coastlines("50m", edgecolor="grey", linewidth=0.3)
ax.add_feature(cfeature.STATES, edgecolor="grey", linewidth=0.5)
skip = 50

# cs = ax.contour(
#     lons,
#     lats,
#     gaussian_filter(ds['gh'].values, sigma=2.4) / 10,
#     var_attrs[var]["levels"]["raw"],
#     colors="k",
#     linewidths=1.0,
#     linestyles="solid",
#     transform=ccrs.PlateCarree(),
# )
# cb = plt.clabel(
#     cs,
#     fontsize=7,
#     inline=1,
#     inline_spacing=10,
#     fmt="%i",
#     rightside_up=True,
#     use_clabeltext=True,
#     zorder=10,
#     colors=["#ffffff", "#ffffff", "#ffffff", "#000000", "#000000", "#000000"],
# )
# Set up station plotting using only every third
# element from arrays for plotting
stationplot = StationPlot(
    ax,
    lons[::skip, ::skip].ravel(),
    lats[::skip, ::skip].ravel(),
    transform=ccrs.PlateCarree(),
    fontsize=12,
)

# Plot markers then data around marker for calculation purposes
ax.scatter(
    lons[::skip, ::skip].ravel(),
    lats[::skip, ::skip].ravel(),
    marker="o",
    transform=ccrs.PlateCarree(),
    zorder=10,
    s=10,
)
stationplot.plot_parameter(
    (0, 1), ds["gh"].values[::skip, ::skip].ravel(), zorder=10, fontsize=8
)
# stationplot.plot_parameter((-1.5, -1), ds['u'].values[::skip, ::skip].ravel(),
#                            formatter='.1f', fontsize = 8)
# stationplot.plot_parameter((1.5, -1), ds['v'].values[::skip, ::skip].ravel(),
#                            formatter='.1f', fontsize = 8)
ax.set_extent([-180, -10, 20, 85], ccrs.PlateCarree())
# ax.set_zorder(1)  # Set zorder for the axis


plt.show()
