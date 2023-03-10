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
from context import json_dir, data_dir


with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

shp_file = str(data_dir) + f"/Roads_Shapefiles/roads_l_v2.shp"
gdf = gpd.read_file(shp_file)
gdf = gdf.to_crs(epsg=4326)


def setBold(txt):
    return r"$\bf{" + str(txt) + "}$"


def open_data(pathlist, i, model, var):
    openTime = datetime.now()
    if (
        any(
            isinstance(i, dict)
            for i in var_attrs[var]["filter_by_keys"][model].values()
        )
        == False
    ):
        ds = xr.open_dataset(
            pathlist[i],
            engine="cfgrib",
            backend_kwargs={"filter_by_keys": var_attrs[var]["filter_by_keys"][model]},
        )
    elif (
        any(
            isinstance(i, dict)
            for i in var_attrs[var]["filter_by_keys"][model].values()
        )
        == True
    ):
        ds_list, keys = [], []
        for filter_by_keys in var_attrs[var]["filter_by_keys"][model]:
            try:
                ds_i = xr.open_dataset(
                    pathlist[i],
                    engine="cfgrib",
                    backend_kwargs={
                        "filter_by_keys": var_attrs[var]["filter_by_keys"][model][
                            filter_by_keys
                        ]
                    },
                )
                if filter_by_keys == "tp":
                    try:
                        ds_ii = xr.open_dataset(
                            pathlist[i - 1],
                            engine="cfgrib",
                            backend_kwargs={
                                "filter_by_keys": var_attrs[var]["filter_by_keys"][
                                    model
                                ][filter_by_keys]
                            },
                        )
                        ds_i = ds_i - ds_ii
                    except:
                        pass
                ds_list.append(ds_i)
                keys.append(filter_by_keys)
            except:
                pass
        ds = xr.merge(ds_list, compat="override")
        print(
            f"Time to load data with filter keys {keys}:  {datetime.now() - openTime}"
        )
    else:
        raise ValueError("Bad filter_by_key options")
    return ds


def config_data(ds, var, case_study, transform=False):
    if len(var_attrs[var]["domain"]) == 2:
        plat, plon = var_attrs[var]["domain"][0], var_attrs[var]["domain"][1]
        center = case_attrs[case_study]["loc"]
        lat, lon = int(center[0]), int(center[1])
        extent = [lon - plon, lon + plon, lat - plat, lat + plat]
        longitude = slice(extent[0] + 360, extent[1] + 360)
        latitude = slice(extent[-1], extent[-2])
    else:
        extent = var_attrs[var]["domain"]
        longitude = slice(169, 351)
        latitude = slice(90, 0)

    if transform == True:
        ## ONLY WORKS FOR GH AT 50 kPa
        ## TODO make this better et up for other climo variables
        ds_climo = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")
        ds_t = ds_climo.salem.transform(ds["gh"].sel(isobaricInhPa=500))
        ds_t = ds_t.sel(longitude=longitude, latitude=latitude)
        ds_climo = ds_climo.sel(longitude=longitude, latitude=latitude)
        vtimes = pd.to_datetime(ds.valid_time.values)
        ds_climo = ds_climo.sel(month=vtimes.month, hour=vtimes.hour)
    else:
        ds_climo, ds_t = None, None

    ds = ds.sel(longitude=longitude, latitude=latitude)

    return ds, ds_climo, ds_t, extent


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


def plot_25kPa(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "25kPa"
    var_name = "gh"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    ds = ds.sel(isobaricInhPa=250)
    fig, gs, ax, lons, lats, vtimes = base_plot(
        ds, ccrs.NorthPolarStereo(central_longitude=-100.0), var
    )
    cs = ax.contour(
        lons,
        lats,
        gaussian_filter(ds[var_name].values, sigma=2.4) / 10,
        var_attrs[var]["levels"]["height"],
        colors="k",
        linewidths=1.0,
        linestyles="solid",
        transform=ccrs.PlateCarree(),
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
        "wxbell", var_attrs[var]["colors"], N=len(var_attrs[var]["levels"])
    )
    norm = matplotlib.colors.Normalize(
        vmin=var_attrs[var]["vmin"], vmax=var_attrs[var]["vmax"] + 1
    )
    u, v = ds["u"].values, ds["v"].values
    wsp = np.sqrt(ds["u"].values ** 2 + ds["v"].values ** 2) * 1.94384
    # new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
    #     ccrs.PlateCarree(), ccrs.NorthPolarStereo(central_longitude=-100.0), u[:2,:2].shape, lons[:2], lats[:2], u[:2,:2], v[:2,:2]
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
    #     color="grey",
    # )
    # ax.quiver(
    # lons, lats, u, v,transform=ccrs.PlateCarree(),
    # )
    cf = ax.contourf(
        lons,
        lats,
        wsp,
        levels=var_attrs[var]["levels"]["speed"],
        colors=var_attrs[var]["colors"],
        norm=norm,
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(var_attrs[var]["unit"], fontsize=10)
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    return


def plot_50kPa(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "50kPa"
    var_name = "gh"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study, transform=True)
    # ds_t = ds_t
    fig, gs, ax, lons, lats, vtimes = base_plot(
        ds_t, ccrs.NorthPolarStereo(central_longitude=-100.0), var
    )
    cs = ax.contour(
        lons,
        lats,
        gaussian_filter(ds_t.values, sigma=2.4) / 10,
        var_attrs[var]["levels"]["raw"],
        colors="k",
        linewidths=1.0,
        linestyles="solid",
        transform=ccrs.PlateCarree(),
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
        "wxbell",
        var_attrs[var]["colors"],
        N=len(var_attrs[var]["levels"]["anomaly"]),
    )
    cf = ax.contourf(
        lons,
        lats,
        ds_t.values - ds_climo[var_name].values,
        var_attrs[var]["levels"]["anomaly"],
        cmap=cmap,
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(var_attrs[var]["unit"], fontsize=10)
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    return


def plot_100_50kPa(ds, case_study, save_dir, *args):
    var = "100-50kPa"
    var_name = "gh"
    figTime = datetime.now()
    dataproj = ccrs.PlateCarree()
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    ds_100_50_kPa = ds[var_name].sel(isobaricInhPa=500) - ds[var_name].sel(
        isobaricInhPa=1000
    )

    mapproj = ccrs.NorthPolarStereo(central_longitude=-100.0)
    fig, gs, ax, lons, lats, vtimes = base_plot(ds_100_50_kPa, mapproj, var)

    # Plot thickness with multiple colors
    clevs = (np.arange(0, 540, 6), np.array([540]), np.arange(546, 700, 6))
    colors = ("tab:blue", "blue", "tab:red")
    linestyles = ("solid", "dashed", "solid")
    kw_clabels = {
        "fontsize": 7,
        "inline": True,
        "inline_spacing": 5,
        "fmt": "%i",
        "rightside_up": True,
        "use_clabeltext": True,
    }
    for clevthick, color, linestyle in zip(clevs, colors, linestyles):
        cs = ax.contour(
            lons,
            lats,
            ds_100_50_kPa / 10,
            levels=clevthick,
            colors=color,
            linewidths=0.8,
            linestyles=linestyle,
            transform=dataproj,
            alpha=0.8,
        )
        plt.clabel(cs, **kw_clabels)

    mslp = gaussian_filter(ds.mslet / 100, sigma=2)
    cs = ax.contour(
        lons,
        lats,
        mslp,
        levels=np.arange(800.0, 1120.0, 4),
        colors="k",
        linewidths=0.8,
        alpha=0.8,
        linestyles="solid",
        transform=dataproj,
        zorder=6,
    )
    cb = plt.clabel(
        cs,
        fontsize=7,
        inline=1,
        inline_spacing=10,
        fmt="%i",
        rightside_up=True,
        use_clabeltext=True,
        zorder=6,
        colors="k",
    )
    ii, ij, jj, ji, = (
        20,
        85,
        80,
        90,
    )

    lonss, latss = np.meshgrid(lons, lats)
    lonss, latss = lonss[ii:-ij, jj:-ji], latss[ii:-ij, jj:-ji]
    # lonss, latss = lonss[b : -b * 2, b : -b * 2], latss[b : -b * 2, b : -b * 2]
    plot_maxmin_points(
        ax,
        lonss,
        latss,
        # mslp[b : -b * 2, b : -b * 2],
        mslp[ii:-ij, jj:-ji],
        "max",
        100,
        symbol="H",
        color="blue",
        transform=dataproj,
    )
    plot_maxmin_points(
        ax,
        lonss,
        latss,
        # mslp[b : -b * 2, b : -b * 2],
        mslp[ii:-ij, jj:-ji],
        "min",
        100,
        symbol="L",
        color="red",
        transform=dataproj,
    )
    try:
        vmin, vmax = var_attrs["tp"]["vmin"], var_attrs["tp"]["vmax"]
        levels, colors = var_attrs["tp"]["levels"], var_attrs["tp"]["colors"]
        unit = var_attrs["tp"]["unit"]
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
        cf = ax.contourf(
            lons,
            lats,
            ds["tp"].values,
            levels=levels,
            colors=colors,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )
    except:
        vmin, vmax = var_attrs["tp"]["vmin"], var_attrs["tp"]["vmax"]
        levels, colors = var_attrs["tp"]["levels"], var_attrs["tp"]["colors"]
        unit = var_attrs["tp"]["unit"]
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
        cf = ax.contourf(
            lons,
            lats,
            np.zeros_like(mslp),
            levels=levels,
            colors=colors,
            norm=norm,
            transform=ccrs.PlateCarree(),
        )

    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    return


def plot_70kPa_RH(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "70kPa-RH"
    var_name = "r"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    ds = ds.sel(isobaricInhPa=700)
    levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    ds[var_name] = xr.where(ds[var_name] > vmax - 1, vmax - 0.1, ds[var_name])
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    cf = ax.contourf(
        lons,
        lats,
        ds[var_name].values,
        levels=levels,
        colors=colors,
        norm=norm,
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.savefig(
        str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
    plt.close()
    return


def plot_wspwdir(ds, case_study, save_dir, height, *args):
    figTime = datetime.now()
    var = "wsp"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
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
    else:
        raise ValueError(f"Invalid height option: {height}, try 10m or 100m")

    wsp = np.sqrt((u ** 2 + v ** 2))
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
        ccrs.PlateCarree(), ccrs.PlateCarree(), u.shape, lons, lats, u, v
    )
    # ax.streamplot(
    #     x=lons,
    #     y=lats,
    #     u=u10,
    #     v=v10,
    #     transform=ccrs.PlateCarree(),
    #     linewidth=0.5,
    #     arrowsize=0.8,
    #     density=1.1,
    #     color="k",
    # )
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
    # )
    Axes.streamplot(
        ax=ax,
        x=new_x,
        y=new_y,
        u=new_u,
        v=new_v,
        transform=ccrs.PlateCarree(),
        linewidth=0.5,
        arrowsize=0.8,
        density=1.1,
        color="k",
    )
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "wxbell", colors, N=len(levels)
    )
    cf = ax.contourf(
        lons, lats, wsp, levels=levels, cmap=cmap, transform=ccrs.PlateCarree()
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
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
        str(save_dir) + f"/{var}-{height}-{vtimes.strftime('%Y%m%d%H')}.png",
        dpi=250,
        bbox_inches="tight",
    )
    print(f"Time to create {var.upper()} {height} fig: ", datetime.now() - figTime)
    plt.close()

    return


def plot_t2m(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "t2m"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    levels, colors = var_attrs[var]["levels"]["raw"], var_attrs[var]["colors"]["raw"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    cf = ax.contourf(
        lons,
        lats,
        ds[var].values - 273.15,
        levels=levels,
        colors=colors,
        norm=norm,
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
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
    plt.close()
    return


def plot_r2(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "r2"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    levels, colors = var_attrs[var]["levels"], var_attrs[var]["colors"]
    vmin, vmax = var_attrs[var]["vmin"], var_attrs[var]["vmax"]
    unit = var_attrs[var]["unit"]
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
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
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
    plt.close()
    return


def plot_tp(ds, case_study, save_dir, *args):
    var = "tp"
    figTime = datetime.now()
    dataproj = ccrs.PlateCarree()
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
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
        cax = plt.subplot(gs[1])
        clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
        clb.ax.set_title(unit, fontsize=10)
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
    plt.close()
    return


def plot_cape(ds, case_study, save_dir, *args):
    figTime = datetime.now()
    var = "cape"
    ds, ds_climo, ds_t, extent = config_data(ds, var, case_study)
    vmin, vmax, step = (
        var_attrs[var]["vmin"],
        var_attrs[var]["vmax"],
        var_attrs[var]["step"],
    )
    levels, colors = np.arange(vmin, vmax, step), var_attrs[var]["colors"]
    unit = var_attrs[var]["unit"]
    fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "wxbell",
        colors,
        N=len(levels),
    )
    cf = ax.contourf(
        lons,
        lats,
        ds[var].values,
        levels=levels,
        cmap=cmap,
        transform=ccrs.PlateCarree(),
    )
    cax = plt.subplot(gs[1])
    clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
    clb.ax.set_title(unit, fontsize=10)
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
    plt.close()
    return


def plot_maxmin_points(
    ax,
    lon,
    lat,
    data,
    extrema,
    nsize,
    symbol,
    color="k",
    plotValue=True,
    transform=None,
):
    """
    This function will find and plot relative maximum and minimum for a 2D grid. The function
    can be used to plot an H for maximum values (e.g., High pressure) and an L for minimum
    values (e.g., low pressue). It is best to used filetered data to obtain  a synoptic scale
    max/min value. The symbol text can be set to a string value and optionally the color of the
    symbol and any plotted value can be set with the parameter color
    lon = plotting longitude values (2D)
    lat = plotting latitude values (2D)
    data = 2D data that you wish to plot the max/min symbol placement
    extrema = Either a value of max for Maximum Values or min for Minimum Values
    nsize = Size of the grid box to filter the max and min values to plot a reasonable number
    symbol = String to be placed at location of max/min value
    color = String matplotlib colorname to plot the symbol (and numerica value, if plotted)
    plot_value = Boolean (True/False) of whether to plot the numeric value of max/min point
    The max/min symbol will be plotted on the current axes within the bounding frame
    (e.g., clip_on=True)
    """
    from scipy.ndimage.filters import maximum_filter, minimum_filter

    if extrema == "max":
        data_ext = maximum_filter(data, nsize, mode="nearest")
    elif extrema == "min":
        data_ext = minimum_filter(data, nsize, mode="nearest")
    else:
        raise ValueError("Value for hilo must be either max or min")

    mxy, mxx = np.where(data_ext == data)

    for i in range(len(mxy)):
        ax.text(
            lon[mxy[i], mxx[i]],
            lat[mxy[i], mxx[i]],
            symbol,
            color=color,
            size=14,
            clip_on=True,
            horizontalalignment="center",
            verticalalignment="center",
            transform=transform,
            zorder=10,
        )
        ax.text(
            lon[mxy[i], mxx[i]],
            lat[mxy[i], mxx[i]],
            "\n" + str(int(data[mxy[i], mxx[i]])),
            color=color,
            size=9,
            clip_on=True,
            fontweight="bold",
            horizontalalignment="center",
            verticalalignment="top",
            transform=transform,
            zorder=10,
        )

    return
