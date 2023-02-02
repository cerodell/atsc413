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

levels = np.arange(0, 6000, 100)
cmap = cm.get_cmap("seismic", 101)  # PiYG

hex_list = []
for i in range(cmap.N):
    rgba = cmap(i)
    # rgb2hex accepts rgb or rgba
    hex_list.append(matplotlib.colors.rgb2hex(rgba))


model = "gfs"
case_study = "high_level"
pathlist = sorted(Path(str(data_dir) + f"/{model}/{case_study}/").glob(f"*.grib2"))
save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)


shp_file = str(data_dir) + f"/Roads_Shapefiles/roads_l_v2.shp"
gdf = gpd.read_file(shp_file)
gdf = gdf.to_crs(epsg=4326)

# gdf = salem.read_shapefile(shp_file)
# reader = shpreader.Reader(shp_file)

# print(reader.schema)


# ds_roads = salem.open_xr_dataset(
#     shp_file
# )

# levels = np.arange(0,270,18)
# levels = np.linspace(0,252,18).astype(int)

# np.linspace(0,272,18).astype(int)
# clev250 = np.arange(9000, 12000+60, 60)/10


# ds = open_data(pathlist, 1, model, "all_vars")


# %%
pathlist = pathlist[:1]
for i in range(len(pathlist)):
    # i = 0
    ds = open_data(pathlist, i, model, "all_vars")

    # %%
    var = "tp"
    figTime = datetime.now()
    dataproj = ccrs.PlateCarree()
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    # %%
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    try:
        vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
        levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
        unit = var_attrs[var]["unit"]
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
        cf = ax.contourf(
            lons,
            lats,
            ds[var].values,
            levels=levels,
            colors=colors,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )
    except:
        vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
        levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
        unit = var_attrs[var]["unit"]
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
        cf = ax.contourf(
            lons,
            lats,
            np.zeros_like(ds.t2m),
            levels=levels,
            colors=colors,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )

    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    # shape_feature = ShapelyFeature(Reader(shp_file).geometries(),
    #                             ccrs.PlateCarree(), facecolor='k')
    # ax.add_feature(shape_feature, crs=ccrs.PlateCarree())
    # ax.add_geometries(Reader(shp_file).geometries(),
    #                     ccrs.PlateCarree(),
    #                     edgecolor="k",
    #                     alpha=0.8,
    #                     facecolor="none",
    #                     lw=10.0,
    #                     zorder=10,)
    ax.add_geometries(
        gdf["geometry"],
        crs=ccrs.PlateCarree(),
        zorder=10,
        linewidth=0.2,
        edgecolor="black",
        facecolor="none",
    )

    ax.set_extent(extent, ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.show()
    # %%
