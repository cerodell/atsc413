import context
import os
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


def solve_W_WD(ds):

    ## Define the latitude and longitude arrays in degrees
    lons_rad = np.deg2rad(ds["latitude"])
    lats_rad = np.deg2rad(ds["longitude"])
    lons_rad, lats_rad = np.meshgrid(lats_rad, lons_rad)

    ## Calculate rotation angle
    theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    ## Calculate sine and cosine of rotation angle
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["u"]
    v_domain = ds["v"]

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta
    ds["u_earth"] = u_earth
    ds["v_earth"] = v_earth

    ## Solve for wind speed
    wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["wsp"] = wsp

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    ds["wdir"] = wdir

    return ds


def open_data(pathlist, i, model, var):
    bashCommand = f" rm -rf {str(pathlist[i]).rsplit('/', 1)[0]}/*.idx"
    os.system(bashCommand)
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
                ).chunk("auto")
                # if filter_by_keys == "tp":
                #     try:
                #         ds_ii = xr.open_dataset(
                #             pathlist[i - 1],
                #             engine="cfgrib",
                #             backend_kwargs={
                #                 "filter_by_keys": var_attrs[var]["filter_by_keys"][
                #                     model
                #                 ][filter_by_keys]
                #             },
                #         )
                #         print(float(ds_i['tp'].mean()))
                #         print(float(ds_ii['tp'].mean()))
                #         ds_i['tp'] = ds_i['tp'] - ds_ii['tp']
                #         print(float(ds_i['tp'].mean()))
                #     except:
                #         pass

                ds_list.append(ds_i)
                keys.append(filter_by_keys)
            except:
                pass
        ds = xr.merge(ds_list, compat="override")
        # ds = xr.combine_by_coords(ds_list, compat="override")
        ds = solve_W_WD(ds)
        print(
            f"Time to load data with filter keys {keys}:  {datetime.now() - openTime}"
        )
    else:
        raise ValueError("Bad filter_by_key options")
    return ds


def config_data(ds, var, case_study, anomaly=False, **kwargs):
    if len(var_attrs[var]["domain"]) == 2:
        plat, plon = var_attrs[var]["domain"][0], var_attrs[var]["domain"][1]
        # print(kwargs)
        try:
            if "".join([i for i in kwargs["height"] if not i.isdigit()]) == "kPa":
                # scale = int(''.join(c for c in kwargs['height'] if c.isdigit()))
                # print(scale)
                plat, plon = (
                    var_attrs[var]["domain"][0] + 12,
                    var_attrs[var]["domain"][1] + 16,
                )
        except:
            pass
        center = case_attrs[case_study]["loc"]
        lat, lon = int(center[0]), int(center[1])
        extent = [lon - plon, lon + plon, lat - plat, lat + plat]
        longitude = slice(extent[0] + 360, extent[1] + 360)
        latitude = slice(extent[-1], extent[-2])
    else:
        center = case_attrs[case_study]["loc"]
        extent = var_attrs[var]["domain"]
        longitude = slice(169, 351)
        latitude = slice(90, 0)

    if anomaly == True:
        ## ONLY WORKS FOR GH AT 50 kPa
        ds_climo = salem.open_xr_dataset(str(data_dir) + "/climatology-1991-2021.nc")
        ds_t = ds_climo.salem.transform(ds["gh"].sel(isobaricInhPa=500))
        ds_t = ds_t.sel(longitude=longitude, latitude=latitude)
        ds_climo = ds_climo.sel(longitude=longitude, latitude=latitude)
        vtimes = pd.to_datetime(ds.valid_time.values)
        # ds_climo = ds_climo.sel(month=vtimes.month, hour=vtimes.hour)
        ## NOTE Add a hacky interpolation method for crossing between month. this could be better, not research study worthy
        day = vtimes.day
        if day < 15:
            month_delta = -1
        else:
            month_delta = 1
        ctime = pd.to_datetime(ds.valid_time.values) + pd.Timedelta(
            days=month_delta * 30
        )

        ds_climo = ds_climo.sel(month=[vtimes.month, ctime.month], hour=vtimes.hour)[
            "gh"
        ]
        ds_climo["month"] = np.array([0, 31])
        ds_climo = ds_climo.interp(month=np.arange(0, 31, 1)).isel(month=day - 1)

    else:
        ds_climo, ds_t = None, None

    ds = ds.sel(longitude=longitude, latitude=latitude)

    return ds, ds_climo, ds_t, extent, center


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


def plot_25kPa(ds, case_study, save_dir, roads=False, *args):
    var = "25kPa"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        var_name = "gh"
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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
        # u, v = ds["u"].values, ds["v"].values
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
        ax.scatter(
            center[1],
            center[0],
            s=40,
            marker="*",
            color="red",
            transform=ccrs.PlateCarree(),
            zorder=10,
        )

        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_50kPa(ds, case_study, save_dir, roads=False, *args):
    var = "50kPa"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        var_name = "gh"
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=True
        )
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
            # ds_t.values - ds_climo[var_name].values,
            ds_t.values - ds_climo.values,
            var_attrs[var]["levels"]["anomaly"],
            cmap=cmap,
            transform=ccrs.PlateCarree(),
        )
        cax = plt.subplot(gs[1])
        clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
        clb.ax.set_title(var_attrs[var]["unit"], fontsize=10)
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
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_85kPa(ds, case_study, save_dir, roads=False, *args):
    var = "85kPa"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        var_name = "gh"
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False, height=var
        )
        ds = ds.sel(isobaricInhPa=850)
        # ds_t = ds_t
        fig, gs, ax, lons, lats, vtimes = base_plot(ds, ccrs.PlateCarree(), var)
        # cs = ax.contour(
        #     lons,
        #     lats,
        #     gaussian_filter(ds_t.values, sigma=2.4) / 10,
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
        # cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        #     "wxbell",
        #     var_attrs[var]["colors"],
        #     N=len(var_attrs[var]["levels"]["anomaly"]),
        # )
        cf = ax.contourf(
            lons,
            lats,
            ds.gh.values / 10,
            np.arange(120, 185, 5),
            cmap="coolwarm",
            transform=ccrs.PlateCarree(),
        )
        cax = plt.subplot(gs[1])
        clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
        clb.ax.set_title(var_attrs[var]["unit"], fontsize=10)
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
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_100_50kPa(ds, case_study, save_dir, roads=False, *args):
    var = "100-50kPa"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        var_name = "gh"
        dataproj = ccrs.PlateCarree()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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
        ax.scatter(
            center[1],
            center[0],
            s=40,
            marker="*",
            color="red",
            transform=ccrs.PlateCarree(),
            zorder=10,
        )
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_70kPa_RH(ds, case_study, save_dir, roads=False, *args):
    var = "70kPa-RH"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        var_name = "r"
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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
        ax.scatter(
            center[1],
            center[0],
            s=40,
            marker="*",
            color="red",
            transform=ccrs.PlateCarree(),
            zorder=10,
        )
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_wspwdir(ds, case_study, save_dir, height, roads=False, **kwargs):
    var = "wsp"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{height}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
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

        # def convert_longitudes(longitudes):
        #     converted_longitudes = np.where(longitudes > 180, longitudes - 360, longitudes)
        #     return converted_longitudes

        # lons = convert_longitudes(lons)
        # new_x, new_y, new_u, new_v, = vector_scalar_to_grid(
        #     ccrs.PlateCarree(), ccrs.PlateCarree(), u.shape, lons, lats, u, v
        # )
        lons, lats = np.meshgrid(lons, lats)

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
        skip = 4
        ax.quiver(
            x=lons[::skip, ::skip],
            y=lats[::skip, ::skip],
            u=u[::skip, ::skip],
            v=v[::skip, ::skip],
            transform=ccrs.PlateCarree(),
            width=0.0010,
            headwidth=5,
            # headwidth=0.8,
            # density=1,
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
        # )
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
        plt.savefig(
            str(save_dir) + f"/{var}-{height}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} {height} fig: ", datetime.now() - figTime)
        plt.close()

    return


def plot_t2m(ds, case_study, save_dir, roads=False, *args):
    var = "t2m"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
        levels, colors = (
            var_attrs[var]["levels"]["raw"],
            var_attrs[var]["colors"]["raw"],
        )
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
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_r2(ds, case_study, save_dir, roads=False, *args):
    var = "r2"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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

        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_tp(ds, case_study, save_dir, roads=False, *args):
    var = "atp"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        dataproj = ccrs.PlateCarree()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()

        var = "tp"
        figTime = datetime.now()
        dataproj = ccrs.PlateCarree()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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
        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
        plt.close()
    return


def plot_cape(ds, case_study, save_dir, roads=False, *args):
    var = "cape"
    if os.path.exists(
        str(save_dir)
        + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
    ):
        pass
    else:
        figTime = datetime.now()
        ds, ds_climo, ds_t, extent, center = config_data(
            ds, var, case_study, anomaly=False
        )
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

        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
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
