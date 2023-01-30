import context
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
from scipy.ndimage.filters import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

from datetime import datetime
from context import data_dir, img_dir


model = "gfs"
case_study = "high_level"

pathlist = sorted(Path(str(data_dir) + f"/{model}/{case_study}/").glob(f"gfs*"))

ds_climatology = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")


save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)

# path = pathlist[4]
# # Import data
# grib_data = cfgrib.open_datasets(path)
# for i in range(len(grib_data)):
#     print('----------')
#     print(i)
#     print(list(grib_data[i]))


# grib_data[4]


def setBold(txt):
    return r"$\bf{" + txt + "}$"


# Download and add the states and coastlines
states = NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_shp",
)


for path in pathlist[0::2]:
    print(path)
    figTime = datetime.now()
    ds = xr.merge(
        [
            xr.open_dataset(
                path,
                engine="cfgrib",
                backend_kwargs={
                    "filter_by_keys": {
                        "typeOfLevel": "heightAboveGround",
                        "shortName": "10u",
                    }
                },
            ),
            xr.open_dataset(
                path,
                engine="cfgrib",
                backend_kwargs={
                    "filter_by_keys": {
                        "typeOfLevel": "heightAboveGround",
                        "shortName": "10v",
                    }
                },
            ),
        ]
    )
    # ds = ds_climatology.salem.transform(ds)

    ds = ds.sel(longitude=slice(235, 255), latitude=slice(62, 48))
    # ds_climatology = ds_climatology.sel(longitude = slice(241,247), latitude = slice(60,54))

    lons, lats, vtimes, itime, stime = (
        ds.longitude.values,
        ds.latitude.values,
        pd.to_datetime(ds.valid_time.values),
        pd.to_datetime(ds.time.values),
        str(int(ds.step.values.astype(float) / 3.6e12)),
    )

    u10 = ds.u10.values * 3.6
    v10 = ds.v10.values * 3.6
    wsp = np.sqrt((u10 ** 2 + v10 ** 2))
    # v10 = gaussian_filter(v10, sigma=2.4)

    # kPa50_anom = ds_climatology.gh.sel(month=vtimes.month, hour=vtimes.hour)

    datacrs = ccrs.PlateCarree()
    plotcrs = ccrs.NorthPolarStereo(central_longitude=-100.0)

    itime.weekday()

    itime.strftime("%HZ %a %d %b %Y")

    fig = plt.figure(1, figsize=(8.0, 5.5))
    gs = gridspec.GridSpec(
        2, 1, height_ratios=[1, 0.02], bottom=0.07, top=0.99, hspace=0.01, wspace=0.01
    )

    ax = plt.subplot(gs[0], projection=datacrs)
    # ax = plt.subplot(gs[0])
    ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left")
    ax.set_title(
        f"{setBold('Hour')}: {stime.zfill(3)}  {setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
        loc="right",
    )
    plt.figtext(
        0.12,
        1,
        setBold("GFS")
        + " "
        + setBold("0.25")
        + r"$^o$"
        + f" 10m Wind Speed and  Direction",
        fontsize=14,
    )

    #   ax.set_extent([west long, east long, south lat, north lat])
    # ax.set_extent([-119, -113, 54, 60], ccrs.PlateCarree())

    ax.coastlines("50m", edgecolor="black", linewidth=0.6)
    ax.add_feature(states, linewidth=0.3, edgecolor="black")

    # ax.quiver(lons, lats, u10, v10, zorder = 10, color="k",transform=datacrs
    # # linewidth=0.3,
    # # arrowsize=0.5,
    # # density=1.4,
    # )
    new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
        ccrs.PlateCarree(), ccrs.PlateCarree(), u10.shape, lons, lats, u10, v10
    )
    # lw = 5*wsp / wsp.max()

    Axes.streamplot(
        ax,
        new_x,
        new_y,
        new_u,
        new_v,
        transform=ccrs.PlateCarree(),
        linewidth=0.5,
        arrowsize=0.8,
        density=1.1,
        color="k",
    )

    levels = np.arange(0, 210, 10)
    colors = [
        "#FFFFFF",
        "#BBBBBB",
        "#646464",
        "#1563D3",
        "#2883F1",
        "#50A5F5",
        "#97D3FB",
        "#0CA10D",
        "#37D33C",
        "#97F58D",
        "#B5FBAB",
        "#FFE978",
        "#FFC03D",
        "#FFA100",
        "#FF3300",
        "#C10000",
        "#960007",
        "#643C32",
    ]
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "meteoblue", colors, N=len(levels)
    )
    cf = ax.contourf(lons, lats, wsp, levels, cmap=cmap, transform=datacrs)

    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title("(km/h)", fontsize=10)
    plt.savefig(
        str(save_dir) + f"/wsp-dir-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print("Make Fig Time: ", datetime.now() - figTime)


# ds = xr.open_dataset(
#     str(data_dir) + f"/nam_218_20190516_0000_000.grb2", engine="cfgrib",
#         backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName':'gh' }}
# ).sel(isobaricInhPa = 500)
