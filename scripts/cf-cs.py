#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import json
import numpy as np
import pandas as pd
import xarray as xr
import cfgrib

from pathlib import Path


import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid
from matplotlib.axes import Axes

import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import xarray as xr

import metpy.calc as mpcalc
from metpy.units import units

from metpy.cbook import get_test_data
from metpy.interpolate import cross_section

from datetime import datetime
from context import data_dir, img_dir, json_dir, root_dir
from utils.plot import base_plot, open_data, config_data
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


############################################################
## LOW LEVEL JET
# https://www.theweatherprediction.com/habyhints2/696/
############################################################
with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

case_study = "kimiwan_complex"
model = "gfs"

loc = case_attrs[case_study]["loc"]
# start = (64, -108.0)
# end = (52, -122.0)
start = (57.2130, -114.9450)
end = (51.2328, -119.3514)
# start = (58.305, -108.0)
# end = (58.305, -122.0)
# pathlist = pathlist[7:8]

fct_days = pd.date_range(
    case_attrs[case_study]["fct_days"][0], case_attrs[case_study]["fct_days"][1]
)

# int_dir = getdata.int_dir
print(case_study)

for fct_day in fct_days[:1]:
    int_dir = fct_day.strftime("%Y%m%dT%H")
    pathlist = sorted(
        Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
    )
    for i in range(len(pathlist[:1])):
        # print(path)
        # %%
        int_time = int_dir.replace("T", "Z")
        save_dir = Path(str(img_dir) + f"/{case_study}/{model}/{int_time}/")
        save_dir.mkdir(parents=True, exist_ok=True)

        ds = open_data(pathlist, i, model, "all_vars")
        ds["longitude"] = ds["longitude"] - 360
        ds["isobaricInhPa"].attrs["units"] = "hPa"

        data = ds.metpy.parse_cf().squeeze()
        data = data.sel(
            longitude=slice(end[1] - 30, start[1] + 30), latitude=slice(80, 30)
        )
        # data["longitude"] = data["longitude"] - 360

        ds_cross = cross_section(data, start, end).set_coords(("latitude", "longitude"))

        ds_cross["Potential_temperature"] = mpcalc.potential_temperature(
            ds_cross["isobaricInhPa"], ds_cross["t"]
        )
        # ds_cross = ds_cross.sel(isobaricInhPa=slice(200, 1000))
        ds_cross = ds_cross.sel(isobaricInhPa=slice(1000, 200))
        ds_cross["wsp"] = (ds_cross["u"] ** 2 + ds_cross["v"] ** 2) ** 0.5  # * 3.6
        # ds_cross['u_wind'] = ds_cross['u_wind'].metpy.convert_units('knots')
        # ds_cross['v_wind'] = ds_cross['v_wind'].metpy.convert_units('knots')
        ds_cross["t_wind"], ds_cross["n_wind"] = mpcalc.cross_section_components(
            ds_cross["u"], ds_cross["v"]
        )

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
        # Plot potential temperature using contour, with some custom labeling
        # theta_contour = ax.contour(ds_cross['longitude'], ds_cross['isobaricInhPa'], ds_cross['Potential_temperature'],
        #                         levels=np.arange(250, 450, 5), colors='k', linewidths=1)
        # theta_contour.clabel(theta_contour.levels[1::2], fontsize=8, colors='k', inline=1,
        #                     inline_spacing=8, fmt='%i K', rightside_up=True, use_clabeltext=True)
        theta_contour = ax.contour(
            ds_cross["longitude"],
            ds_cross["isobaricInhPa"] / 10,
            ds_cross["gh"] - ds_cross["gh"].mean(dim="index"),
            levels=np.arange(-100, 100, 10),
            colors="k",
            linewidths=1,
        )

        theta_contour.clabel(
            theta_contour.levels[1::2],
            fontsize=8,
            colors="k",
            inline=1,
            inline_spacing=8,
            fmt="%i Δm",
            rightside_up=True,
            use_clabeltext=True,
        )
        cf = ax.contourf(
            ds_cross.longitude,
            ds_cross.isobaricInhPa / 10,
            ds_cross["wsp"],
            levels=np.floor(np.array(levels) / 3.6),
            cmap=cmap,
            extend="max",
        )

        ax.axvline(x=loc[1], color="red", linestyle="--", lw=0.5, zorder=2)

        # ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_yscale("symlog")
        ax.set_yticklabels(np.arange(100, 10, -10))
        ax.set_ylim(
            ds_cross["isobaricInhPa"].max() / 10, ds_cross["isobaricInhPa"].min() / 10
        )
        ax.set_yticks(np.arange(100, 10, -10))

        ds_cross["sp"] = ds_cross["sp"].metpy.convert_units("hPa")

        ax.fill_between(
            ds_cross["longitude"],
            ds_cross["isobaricInhPa"].sel(isobaricInhPa=1000) / 10,
            ds_cross["sp"] / 10,
            color="sienna",
            zorder=10,
        )

        # Define the CRS and inset axes
        data_crs = data["gh"].metpy.cartopy_crs
        ax_inset = fig.add_axes([-0.18, 0.6, 0.3, 0.3], projection=data_crs)

        # Plot geopotential height at 500 hPa using xarray's contour wrapper
        cf_hg = ax_inset.contourf(
            data["longitude"],
            data["latitude"],
            data["gh"].sel(isobaricInhPa=850) / 10,
            levels=np.arange(115, 160, 5),
            cmap="coolwarm",
            extend="both",
        )

        cbar = plt.colorbar(cf_hg, ax=ax_inset, pad=0.0004, location="left")
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
        ax_inset.scatter(
            loc[1],
            loc[0],
            zorder=2,
            s=40,
            marker="*",
            color="red",
            edgecolors="black",
            linewidth=0.8,
        )

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
            + "Change in Geopotential Height and Wind Speed",
            fontsize=14,
        )
        plt.show()
        # plt.savefig(
        #     str(save_dir) + f"/cross-wsp-{vtimes.strftime('%Y%m%d%H')}.jpeg",
        #     dpi=250,
        #     bbox_inches="tight",
        # )


# %%
