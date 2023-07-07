import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path


import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage.filters import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.io.shapereader as shpreader


from datetime import datetime
from context import data_dir, img_dir, json_dir
from utils.plot import base_plot, open_data, config_data

levels = np.arange(-450, 468, 18)

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


from pylab import *


height = "85kPa"

test = "".join([i for i in height if not i.isdigit()])

test2 = int("".join(c for c in height if c.isdigit())) * 10

levels = np.arange(0, 6000, 100)
cmap = cm.get_cmap("seismic", 101)  # PiYG

hex_list = []
for i in range(cmap.N):
    rgba = cmap(i)
    # rgb2hex accepts rgb or rgba
    hex_list.append(matplotlib.colors.rgb2hex(rgba))


case_study = "sparks_lake"
model = "gfs"
int_dir = "20210625T00"

pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
)
# save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
# save_dir.mkdir(parents=True, exist_ok=True)


shp_file = str(data_dir) + f"/Roads_Shapefiles/roads_l_v2.shp"
gdf = gpd.read_file(shp_file)
gdf = gdf.to_crs(epsg=4326)


pathlist = pathlist[:1]
for i in range(len(pathlist)):
    # i = 0
    ds = open_data(pathlist, i, model, "all_vars")
    # %%
    # figTime = datetime.now()
    var = "wsp"
    roads = False
    ds, ds_climo, ds_t, extent, center = config_data(
        ds, var, case_study, anomaly=False, height=height
    )
    levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    var_attrs[var]["title"] = height + " " + var_attrs["wsp"]["title"][-25:]
    if height == "10m":
        u = ds.u10.values * 3.6
        v = ds.v10.values * 3.6
    elif height == "100m":
        u = ds.u100.values * 3.6
        v = ds.v100.values * 3.6
    elif "".join([i for i in height if not i.isdigit()]) == "kPa":
        hPa = int("".join(c for c in height if c.isdigit())) * 10
        u = ds.u.sel(isobaricInhPa=hPa).values * 3.6
        v = ds.v.sel(isobaricInhPa=hPa).values * 3.6
    else:
        raise ValueError(f"Invalid height option: {height}, try 10m or 100m")

    wsp = np.sqrt((u ** 2 + v ** 2))
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)

    def convert_longitudes(longitudes):
        converted_longitudes = np.where(longitudes > 180, longitudes - 360, longitudes)
        return converted_longitudes

    lons = convert_longitudes(lons)
    new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
        ccrs.PlateCarree(), ccrs.PlateCarree(), u.shape, lons, lats, u, v
    )
    # lons, lats = np.meshgrid(lons, lats)

    # ax.streamplot(
    #     x=lons,
    #     y=lats,
    #     u=u,
    #     v=v,
    #     transform=ccrs.PlateCarree(),
    #     linewidth=0.5,
    #     arrowsize=0.8,
    #     # density=4,
    #     color="k",
    #     zorder = 10
    # )
    # skip = 4
    # ax.quiver(
    #     x=lons[::skip, ::skip],
    #     y=lats[::skip, ::skip],
    #     u=u[::skip, ::skip],
    #     v=v[::skip, ::skip],
    #     transform=ccrs.PlateCarree(),
    #     width=0.0010,
    #     headwidth=5,
    #     # headwidth=0.8,
    #     # density=1,
    #     color="k",
    #     zorder=10,
    # )
    ax.streamplot(
        x=new_x,
        y=new_y,
        u=new_u,
        v=new_v,
        transform=ccrs.PlateCarree(),
        linewidth=0.5,
        arrowsize=0.8,
        density=100,
        color="k",
    )
    # Axes.streamplot(
    #     ax=ax,
    #     x=new_x,
    #     y=new_y,
    #     u=new_u,
    #     v=new_v,
    #     transform=ccrs.PlateCarree(),
    #     linewidth=0.5,
    #     arrowsize=0.8,
    #     density=1.1,
    #     color="k",
    # )
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "wxbell", colors, N=len(levels)
    )
    cf = ax.contourf(
        lons, lats, wsp, levels=levels, cmap=cmap, transform=ccrs.PlateCarree()
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    if roads == True:
        ax.add_geometries(
            gdf["geometry"],
            crs=ccrs.PlateCarree(),
            zorder=10,
            linewidth=0.2,
            edgecolor="black",
            facecolor="none",
        )

    ax.set_extent(extent, ccrs.PlateCarree())
    ax.scatter(
        center[1],
        center[0],
        s=40,
        marker="*",
        color="red",
        transform=ccrs.PlateCarree(),
        zorder=10,
    )
    # plt.savefig(
    #     str(save_dir) + f"/{var}-{height}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
    #     dpi=250,
    #     bbox_inches="tight",
    # )
    # print(f"Time to create {var.upper()} {height} fig: ", datetime.now() - figTime)
    plt.show()
    # %%

    #     figTime = datetime.now()
    # dataproj = ccrs.PlateCarree()
    # ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    # # %%
    # fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    # try:
    #     vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    #     levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    #     unit = var_attrs[var]["unit"]
    #     norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    #     cf = ax.contourf(
    #         lons,
    #         lats,
    #         ds[var].values,
    #         levels=levels,
    #         colors=colors,
    #         norm=norm,
    #         transform=ccrs.PlateCarree(),
    #     )
    # except:
    #     vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    #     levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    #     unit = var_attrs[var]["unit"]
    #     norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    #     cf = ax.contourf(
    #         lons,
    #         lats,
    #         np.zeros_like(ds.t2m),
    #         levels=levels,
    #         colors=colors,
    #         norm=norm,
    #         transform=ccrs.PlateCarree(),
    #     )

    # cax = plt.subplot(gs[1])
    # clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    # clb.ax.set_title(unit, fontsize=10)
    # # shape_feature = ShapelyFeature(Reader(shp_file).geometries(),
    # #                             ccrs.PlateCarree(), facecolor='k')
    # # ax.add_feature(shape_feature, crs=ccrs.PlateCarree())
    # # ax.add_geometries(Reader(shp_file).geometries(),
    # #                     ccrs.PlateCarree(),
    # #                     edgecolor="k",
    # #                     alpha=0.8,
    # #                     facecolor="none",
    # #                     lw=10.0,
    # #                     zorder=10,)
    # ax.add_geometries(
    #     gdf["geometry"],
    #     crs=ccrs.PlateCarree(),
    #     zorder=10,
    #     linewidth=0.2,
    #     edgecolor="black",
    #     facecolor="none",
    # )

    # ax.set_extent(extent, ccrs.PlateCarree())
    # plt.savefig(
    #     str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
    #     dpi=250,
    #     bbox_inches="tight",
    # )
    # print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    # plt.show()
# %%
