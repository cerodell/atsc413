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
from scipy.ndimage import gaussian_filter
from cartopy.vector_transform import vector_scalar_to_grid

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.io.shapereader as shpreader
from pylab import *


from datetime import datetime
from context import data_dir, img_dir, json_dir
from utils.plot import base_plot, open_data, config_data

levels = np.arange(-450, 468, 18)

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)


height = "85kPa"
case_study = "sparks_lake"
model = "gfs"
int_dir = "20210628T00"

pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
)


save_dir = Path(str(img_dir) + f'/{case_study}/{model}/{int_dir.replace("T", "Z")}/')
save_dir.mkdir(parents=True, exist_ok=True)


shp_file = str(data_dir) + f"/Roads_Shapefiles/roads_l_v2.shp"
gdf = gpd.read_file(shp_file)
gdf = gdf.to_crs(epsg=4326)


# i = 0
ds = open_data(pathlist, 0, model, "all_vars")

# %%
var = "t2m_anomaly"
# if os.path.exists(
#     str(save_dir)
#     + f"/{var}-{pd.to_datetime(ds.valid_time.values).strftime('%Y%m%d%H')}.jpeg"
# ):
#     pass
# else:
figTime = datetime.now()
ds, ds_climo, ds_t, extent, center = config_data(ds, var, case_study, anomaly=True)
# ds_t = ds_t
fig, gs, ax, lons, lats, vtimes = base_plot(
    ds_t, ccrs.NorthPolarStereo(central_longitude=-100.0), var
)
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "wxbell",
    var_attrs[var]["colors"],
    N=len(var_attrs[var]["levels"]["anomaly"]),
)
cf = ax.contourf(
    lons,
    lats,
    gaussian_filter(ds_t.values - (ds_climo.values), sigma=2.4),
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
    edgecolors="black",
    linewidth=0.8,
)
plt.savefig(
    str(save_dir) + f"/{var}-{vtimes.strftime('%Y%m%d%H')}.jpeg",
    dpi=250,
    bbox_inches="tight",
)
print(f"Time to create {var.upper()} fig: ", datetime.now() - figTime)
plt.show()
# del ds
# del ds_climo
# del ds_t
# del fig
# gc.collect()

# %%
