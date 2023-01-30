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
from scipy.ndimage.filters import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

from context import json_dir, data_dir


with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


def setBold(txt):
    return r"$\bf{" + str(txt) + "}$"


def get_data(path, model, var, case_study):
    ds_climo = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")

    if len(var_attrs[var]["domain"]) == 2:
        plat, plon = var_attrs[var]["domain"][0], var_attrs[var]["domain"][1]
        center = case_attrs[case_study]["loc"]
        lat, lon = int(center[0]), int(center[1])
        extent = [lon - plon, lon + plon, lat - plat, lat + plat]
        longitude = slice(extent[0] + 360, extent[1] + 360)
        latitude = slice(extent[-1], extent[-2])
    else:
        extent = var_attrs[var]["domain"]
        # longitude = slice(extent[0]+360, extent[1]+360)
        longitude = slice(169, 351)
        # latitude = slice(extent[-1], extent[-2])
        latitude = slice(90, 0)

    try:
        ds = xr.open_dataset(
            path,
            engine="cfgrib",
            backend_kwargs={"filter_by_keys": var_attrs[var]["filter_by_keys"][model]},
        )
    except:
        ds_list = []
        for filter_by_keys in var_attrs[var]["filter_by_keys"][model]:
            # print(filter_by_keys)
            ds_list.append(
                xr.open_dataset(
                    path,
                    engine="cfgrib",
                    backend_kwargs={
                        "filter_by_keys": var_attrs[var]["filter_by_keys"][model][
                            filter_by_keys
                        ]
                    },
                )
            )
        ds = xr.merge(ds_list)

    ds = ds_climo.salem.transform(ds)
    ds = ds.sel(longitude=longitude, latitude=latitude)
    ds_climo = ds_climo.sel(longitude=longitude, latitude=latitude)

    vtimes = pd.to_datetime(ds.valid_time.values)
    ds_climo = ds_climo.sel(month=vtimes.month, hour=vtimes.hour)

    return ds, ds_climo


def base_plot(ds, plotcrs, var, *args):

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

    fig = plt.figure(
        1, figsize=(var_attrs[var]["figsize"][0], var_attrs[var]["figsize"][1])
    )
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
        0.12,
        1,
        setBold("GFS") + " " + setBold("0.25") + r"$^o$ " + var_attrs[var]["title"],
        fontsize=14,
    )

    ax.coastlines("50m", edgecolor="black", linewidth=0.6)
    ax.add_feature(states, linewidth=0.3, edgecolor="black")

    return fig, gs, ax, lons, lats, vtimes
