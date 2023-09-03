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

from datetime import datetime
from context import data_dir, img_dir, json_dir, root_dir
from utils.plot import base_plot, open_data, config_data
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

case_study = "kimiwan_complex"
model = "gfs"


fct_days = pd.date_range(
    case_attrs[case_study]["fct_days"][0], case_attrs[case_study]["fct_days"][1]
)

# int_dir = getdata.int_dir
print(case_study)

for fct_day in fct_days:
    int_dir = fct_day.strftime("%Y%m%dT%H")
    pathlist = sorted(
        Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
    )
    for i in range(len(pathlist)):
        # print(path)
        int_time = int_dir.replace("T", "Z")
        save_dir = Path(str(img_dir) + f"/{case_study}/{model}/{int_time}/")
        save_dir.mkdir(parents=True, exist_ok=True)

        ds = open_data(pathlist, i, model, "upper")

        # %%
        var = "25kPa-div"
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
            # var_attrs[var]["levels"]["raw"],
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

        ax.streamplot(
            x=lons,
            y=lats,
            u=ds["u"],
            v=ds["v"],
            transform=ccrs.PlateCarree(),
            linewidth=0.5,
            arrowsize=0.8,
            # density=4,
            color="grey",
            zorder=10,
        )

        div_25 = mpcalc.divergence(ds["u"], ds["v"])
        div_25 = gaussian_filter(div_25, sigma=2.4)
        cf = ax.contourf(
            lons,
            lats,
            div_25 * 1e5,
            levels=var_attrs[var]["levels"]["speed"],
            cmap="bwr",
            transform=ccrs.PlateCarree(),
            extend="both",
        )
        cax = plt.subplot(gs[1])
        clb = plt.colorbar(cf, cax=cax, orientation="horizontal")
        clb.ax.set_title(r"($10^{-5} s^{-1}$)", fontsize=10)
        ax.set_extent(extent, ccrs.PlateCarree())

        ax.scatter(
            center[1],
            center[0],
            s=40,
            marker="*",
            color="red",
            transform=ccrs.PlateCarree(),
            zorder=10,
            edgecolors="black",
            linewidth=0.8,
        )

        plt.savefig(
            str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
            dpi=250,
            bbox_inches="tight",
        )
        print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)


# %%
