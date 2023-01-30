import context
import json
import salem
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.ndimage.filters import gaussian_filter

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

from datetime import datetime
from context import data_dir, img_dir, json_dir

levels = np.arange(-450, 468, 18)

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)


model = "gfs"
case_study = "high_level"

len(var_attrs["r2"]["filter_by_keys"][model])

print(
    any(isinstance(i, dict) for i in var_attrs["wsp"]["filter_by_keys"][model].values())
)


pathlist = sorted(Path(str(data_dir) + f"/{model}/{case_study}/").glob(f"*.grib2"))

# Import data
grib_data = cfgrib.open_datasets(pathlist[0])
for i in range(len(grib_data)):
    print("----------")
    print(i)
    print(list(grib_data[i]))

ds = xr.open_dataset(
    pathlist[0],
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {"typeOfLevel": "heightAboveGround", "shortName": "10u"}
    },
)

ds_climatology = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")


save_dir = Path(str(img_dir) + f"/{model}/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)


for path in pathlist[::2]:
    # path = pathlist[4]
    print(path)
    figTime = datetime.now()
    ds = xr.open_dataset(
        path,
        engine="cfgrib",
        backend_kwargs={
            "filter_by_keys": {"typeOfLevel": "isobaricInhPa", "shortName": "gh"}
        },
    ).sel(isobaricInhPa=500)

    ds = ds.drop(["isobaricInhPa"])
    ds = ds_climatology.salem.transform(ds)

    ds = ds.sel(longitude=slice(169, 351), latitude=slice(90, 0))
    ds_climatology = ds_climatology.sel(
        longitude=slice(169, 351), latitude=slice(90, 0)
    )

    lons, lats, vtimes, itime, stime = (
        ds.longitude.values,
        ds.latitude.values,
        pd.to_datetime(ds.valid_time.values),
        pd.to_datetime(ds.time.values),
        str(int(ds.step.values.astype(float) / 3.6e12)),
    )

    kPa50 = ds.gh.values
    kPa50 = gaussian_filter(kPa50, sigma=2.4)

    kPa50_anom = ds_climatology.gh.sel(month=vtimes.month, hour=vtimes.hour)

    datacrs = ccrs.PlateCarree()
    plotcrs = ccrs.NorthPolarStereo(central_longitude=-100.0)

    itime.weekday()

    itime.strftime("%HZ %a %d %b %Y")

    # Download and add the states and coastlines
    states = NaturalEarthFeature(
        category="cultural",
        scale="50m",
        facecolor="none",
        name="admin_1_states_provinces_shp",
    )

    def setBold(txt):
        return r"$\bf{" + str(txt) + "}$"

    fig = plt.figure(1, figsize=(10.0, 5.0))
    gs = gridspec.GridSpec(
        2, 1, height_ratios=[1, 0.02], bottom=0.07, top=0.99, hspace=0.01, wspace=0.01
    )

    ax = plt.subplot(gs[0], projection=plotcrs)
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
        + f" 50-kPa Geopotential Heights (dm) and Anomaly (m)",
        fontsize=14,
    )

    #   ax.set_extent([west long, east long, south lat, north lat])
    ax.set_extent([-170, -10, 18, 75], ccrs.PlateCarree())

    ax.coastlines("50m", edgecolor="black", linewidth=0.6)
    ax.add_feature(states, linewidth=0.3, edgecolor="black")

    levels = np.arange(471, 603, 3)
    cs = ax.contour(
        lons,
        lats,
        kPa50 / 10,
        levels,
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
        # colors = 'k',
        zorder=10,
        colors=["#ffffff", "#ffffff", "#ffffff", "#000000", "#000000", "#000000"],
    )

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "",
        [
            "#879294",
            "#1a6d3c",
            "#c7e992",
            "#7e6ea7",
            "#1f54ad",
            "#ffffff",
            "#ffcf66",
            "#ff4a04",
            "#dc1700",
            "#d91c52",
            "#cb619e",
        ],
    )
    levels = np.arange(-450, 468, 18)
    cf = ax.contourf(
        lons, lats, kPa50 - kPa50_anom, levels, cmap=cmap, transform=datacrs
    )

    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title("(m)", fontsize=10)
    plt.savefig(
        str(save_dir) + f"/50kPa-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print("Make Fig Time: ", datetime.now() - figTime)


# ds = xr.open_dataset(
#     str(data_dir) + f"/nam_218_20190516_0000_000.grb2", engine="cfgrib",
#         backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName':'gh' }}
# ).sel(isobaricInhPa = 500)


# # Import data
# grib_data = cfgrib.open_datasets(str(data_dir) + f"/gfs/gfs.0p25.2019051600.f264.grib2")
# for i in range(len(grib_data)):
#     print('----------')
#     print(i)
#     print(list(grib_data[i]))
