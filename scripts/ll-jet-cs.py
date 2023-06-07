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
int_time = "20190516T00"


pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_time}/").glob(f"*.grib2")
)

save_dir = Path(str(img_dir) + f'/{case_study}/{model}/{int_time.replace("T", "Z")}/')
save_dir.mkdir(parents=True, exist_ok=True)

loc = [58.305, -117.2924]
start = (64, -108.0)
end = (53, -122.0)

# pathlist = pathlist[7:8]
for i in range(len(pathlist)):
    ds = open_data(pathlist, i, model, "all_vars")
    ds["longitude"] = ds["longitude"] - 360
    ds["isobaricInhPa"] = ds["isobaricInhPa"] / 10

    data = ds.metpy.parse_cf().squeeze()
    data = data.sel(longitude=slice(end[1] - 30, start[1] + 30), latitude=slice(80, 30))
    # data["longitude"] = data["longitude"] - 360

    ds_cross = cross_section(data, start, end).set_coords(("latitude", "longitude"))

    # ds_cross["longitude"] = ds_cross["longitude"] - 360
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

    # %%
    fig = plt.figure(figsize=(14, 6))

    ax = fig.add_subplot(1, 1, 1)

    cs = ax.contour(
        ds_cross.longitude,
        ds_cross.isobaricInhPa,
        ds_cross["gh"] / 10,
        colors="k",
        linewidths=1.0,
        linestyles="solid",
        levels=[100, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000],
    )
    cb = plt.clabel(
        cs,
        fontsize=7,
        inline=1,
        inline_spacing=10,
        fmt="%idm",
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
    # ax.scatter(loc[1], 980, zorder=2, s=40, marker="*", color="red")
    ax.axvline(x=loc[1], color="red", linestyle="--", lw=0.5, zorder=2)

    ax.set_ylim(ax.get_ylim()[::-1])

    # Define the CRS and inset axes
    data_crs = data["gh"].metpy.cartopy_crs
    ax_inset = fig.add_axes([-0.14, 0.6, 0.3, 0.3], projection=data_crs)

    # Plot geopotential height at 500 hPa using xarray's contour wrapper
    cf_hg = ax_inset.contourf(
        data["longitude"],
        data["latitude"],
        data["gh"].sel(isobaricInhPa=85) / 10,
        levels=np.arange(115, 160, 5),
        cmap="coolwarm",
        extend="both",
    )

    cbar = plt.colorbar(cf_hg, ax=ax_inset, pad=0.004, location="left")
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label(
        "dm",
        rotation=90,
        fontsize=10,
        labelpad=5,
    )

    endpoints = data_crs.transform_points(
        ccrs.Geodetic(), *np.vstack([start, end]).transpose()[::-1]
    )
    ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c="k", zorder=2)
    ax_inset.plot(ds_cross["longitude"], ds_cross["latitude"], c="k", zorder=2)
    ax_inset.scatter(loc[1], loc[0], zorder=2, s=40, marker="*", color="red")

    # Add geographic features
    ax_inset.coastlines()
    ax_inset.add_feature(
        cfeature.STATES.with_scale("50m"), edgecolor="k", alpha=0.2, zorder=0
    )
    # province boundaries
    provinc_bodr = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
        edgecolor="k",
    )
    ax_inset.add_feature(provinc_bodr, edgecolor="k", alpha=0.2, zorder=10)

    country_bodr = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_0_boundary_lines_land",
        scale="50m",
        facecolor="none",
        edgecolor="k",
    )
    ax_inset.add_feature(country_bodr, edgecolor="k", alpha=0.8, zorder=10)
    ax_inset.set_title("85 kPa Geopotential Heights")

    cbar = plt.colorbar(cf, ax=ax, pad=0.04)
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label(
        "Wind Speed \n" + r"($\mathrm{~m} \mathrm{~s}^{-1}$)",
        rotation=90,
        fontsize=12,
        labelpad=15,
    )

    ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
    ax.set_title(
        f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
        loc="right",
    )
    ax.set_ylabel("Pressure (kPa)", fontsize=12)
    ax.set_xlabel("Longitude (degrees east)", fontsize=12)
    ax.tick_params(axis="both", labelsize=12)

    plt.figtext(
        0.12,
        0.97,
        setBold("GFS")
        + " "
        + setBold("0.25")
        + r"$^o$ "
        + "Geopotential Height and Wind Speed",
        fontsize=14,
    )
    plt.savefig(
        str(save_dir) + f"/cross-wsp-{vtimes.strftime('%Y%m%d%H')}.jpeg",
        dpi=250,
        bbox_inches="tight",
    )

# %%
