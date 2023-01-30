import sys
import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


import matplotlib.colors
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

from datetime import datetime
from utils.plot import base_plot, open_data
from context import json_dir, data_dir, img_dir


with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


model = "gfs"
case_study = "high_level"

# case_study = sys.argv[1]
# model = case_attrs[case_study]["model"]
# print(case_study)


pathlist = sorted(Path(str(data_dir) + f"/{model}/{case_study}/").glob(f"*.grib2"))
save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)

datacrs = ccrs.PlateCarree()
for path in pathlist[:1]:
    print(path)
    ###################### 50 kPa  ######################
    var = "50kPa"
    var_name = "gh"
    figTime = datetime.now()
    ds, ds_climo = open_data(path, model, var, case_study)
    ds = ds.sel(isobaricInhPa=500)
    fig, gs, ax, lons, lats, vtimes = base_plot(
        ds, ccrs.NorthPolarStereo(central_longitude=-100.0), var
    )

    cs = ax.contour(
        lons,
        lats,
        gaussian_filter(ds[var_name].values, sigma=2.4) / 10,
        var_attrs[var]["levels"]["raw"],
        colors="k",
        linewidths=1.0,
        linestyles="solid",
        transform=datacrs,
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
        colors=["#ffffff", "#ffffff", "#ffffff", "#000000", "#000000", "#000000"],
    )
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "wxbell", var_attrs[var]["colors"], N=len(var_attrs[var]["levels"]["anomaly"])
    )
    cf = ax.contourf(
        lons,
        lats,
        ds[var_name].values - ds_climo[var_name].values,
        var_attrs[var]["levels"]["anomaly"],
        cmap=cmap,
        transform=datacrs,
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(var_attrs[var]["unit"], fontsize=10)
    ax.set_extent(var_attrs[var]["domain"], ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    # #####################################################

    #################### WSP WDIR  ######################
    var = "wsp"
    levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    figTime = datetime.now()
    ds, ds_climo = open_data(path, model, var, case_study)
    u10 = ds.u10.values * 3.6
    v10 = ds.v10.values * 3.6
    wsp = np.sqrt((u10 ** 2 + v10 ** 2))

    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
        ccrs.PlateCarree(), ccrs.PlateCarree(), u10.shape, lons, lats, u10, v10
    )
    ax.set_extent(var_attrs["50kPa"]["domain"], ccrs.PlateCarree())
    ax.streamplot(
        x=lons,
        y=lats,
        u=u10,
        v=v10,
        transform=ccrs.PlateCarree(),
        linewidth=0.5,
        arrowsize=0.8,
        density=1.1,
        color="k",
        zorder=10,
    )
    # ax.streamplot(
    #     x = new_x,
    #     y = new_y,
    #     u = new_u,
    #     v = new_v,
    #     transform=ccrs.PlateCarree(),
    #     linewidth=0.5,
    #     arrowsize=0.8,
    #     density=1.1,
    #     color="k",
    #     zorder = 10
    # )
    # Axes.streamplot(
    #     ax = ax,
    #     x = new_x,
    #     y = new_y,
    #     u = new_u,
    #     v = new_v,
    #     transform=ccrs.PlateCarree(),
    #     linewidth=0.5,
    #     arrowsize=0.8,
    #     density=1.1,
    #     color="k",
    #     zorder = 10,
    # )
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "wxbell", colors, N=len(levels)
    )
    cf = ax.contourf(lons, lats, wsp, levels=levels, cmap=cmap, transform=datacrs)
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    # # #####################################################

    ##################### 2m Temp ######################
    var = "t2m"
    levels, colors = var_attrs[var]["levels"]["raw"], var_attrs[var]["colors"]["raw"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    figTime = datetime.now()
    ds, ds_climo = open_data(path, model, var, case_study)
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    cf = ax.contourf(
        lons,
        lats,
        ds[var].values - 273.15,
        levels=levels,
        colors=colors,
        norm=norm,
        transform=datacrs,
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    ###################################################

    ##################### 2m RH ######################
    var = "r2"
    levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    figTime = datetime.now()
    ds, ds_climo = open_data(path, model, var, case_study)
    ds[var] = xr.where(ds[var] > vmax - 1, vmax - 0.1, ds[var])
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    cf = ax.contourf(
        lons,
        lats,
        ds[var].values,
        levels=levels,
        colors=colors,
        norm=norm,
        transform=datacrs,
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    ####################################################
