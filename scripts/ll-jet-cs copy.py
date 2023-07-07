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

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.interpolate import cross_section

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
data = ds.metpy.parse_cf().squeeze()
start = (37.0, -105.0)
end = (35.5, -65.0)
cross = cross_section(data, start, end).set_coords(("latitude", "longitude"))
print(cross)


cross["Potential_temperature"] = mpcalc.potential_temperature(
    cross["isobaricInhPa"], cross["t"]
)
cross["Relative_humidity"] = cross["r"]

# mpcalc.relative_humidity_from_specific_humidity(
#     cross['isobaricInhPa'],
#     cross['t'],
#     cross['Specific_humidity']
# )
cross["u"] = cross["u"].metpy.convert_units("knots")
cross["v"] = cross["v"].metpy.convert_units("knots")
cross["t_wind"], cross["n_wind"] = mpcalc.cross_section_components(
    cross["u"], cross["v"]
)

print(cross)

# %%

# Define the figure object and primary axes
fig = plt.figure(1, figsize=(16.0, 9.0))
ax = plt.axes()

# Plot RH using contourf
rh_contour = ax.contourf(
    cross["longitude"],
    cross["isobaricInhPa"],
    cross["Relative_humidity"],
    levels=np.arange(0, 1.05, 0.05),
    cmap="YlGnBu",
)
rh_colorbar = fig.colorbar(rh_contour)

# Plot potential temperature using contour, with some custom labeling
theta_contour = ax.contour(
    cross["longitude"],
    cross["isobaricInhPa"],
    cross["Potential_temperature"],
    levels=np.arange(250, 450, 5),
    colors="k",
    linewidths=2,
)
theta_contour.clabel(
    theta_contour.levels[1::2],
    fontsize=8,
    colors="k",
    inline=1,
    inline_spacing=8,
    fmt="%i",
    rightside_up=True,
    use_clabeltext=True,
)

# Plot winds using the axes interface directly, with some custom indexing to make the barbs
# less crowded
wind_slc_vert = list(range(0, 19, 2)) + list(range(19, 29))
wind_slc_horz = slice(5, 100, 5)
ax.barbs(
    cross["longitude"][wind_slc_horz],
    cross["isobaricInhPa"][wind_slc_vert],
    cross["t_wind"][wind_slc_vert, wind_slc_horz],
    cross["n_wind"][wind_slc_vert, wind_slc_horz],
    color="k",
)

# Adjust the y-axis to be logarithmic
ax.set_yscale("symlog")
ax.set_yticklabels(np.arange(1000, 50, -100))
ax.set_ylim(cross["isobaricInhPa"].max(), cross["isobaricInhPa"].min())
ax.set_yticks(np.arange(1000, 50, -100))

# Define the CRS and inset axes
data_crs = data["gh"].metpy.cartopy_crs
ax_inset = fig.add_axes([0.125, 0.665, 0.25, 0.25], projection=data_crs)

# Plot geopotential height at 500 hPa using xarray's contour wrapper
ax_inset.contour(
    data["longitude"],
    data["latitude"],
    data["gh"].sel(isobaricInhPa=500.0),
    levels=np.arange(5100, 6000, 60),
    cmap="inferno",
)

# Plot the path of the cross section
endpoints = data_crs.transform_points(
    ccrs.Geodetic(), *np.vstack([start, end]).transpose()[::-1]
)
ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c="k", zorder=2)
ax_inset.plot(cross["longitude"], cross["latitude"], c="k", zorder=2)

# Add geographic features
ax_inset.coastlines()
ax_inset.add_feature(
    cfeature.STATES.with_scale("50m"), edgecolor="k", alpha=0.2, zorder=0
)

# Set the titles and axes labels
ax_inset.set_title("")
ax.set_title(
    f"NARR Cross-Section \u2013 {start} to {end} \u2013 "
    f'Valid: {cross["time"].dt.strftime("%Y-%m-%d %H:%MZ").item()}\n'
    "Potential Temperature (K), Tangential/Normal Winds (knots), Relative Humidity "
    "(dimensionless)\nInset: Cross-Section Path and 500 hPa Geopotential Height"
)
ax.set_ylabel("Pressure (hPa)")
ax.set_xlabel("Longitude (degrees east)")
rh_colorbar.set_label("Relative Humidity (dimensionless)")

plt.show()

# %%
