import sys
import context
import json
from pathlib import Path


from datetime import datetime
from utils.plot import *
from context import json_dir, data_dir, img_dir

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

import cartopy.feature
from cartopy.mpl.patch import geos_to_path
import cartopy.crs as ccrs
import itertools

np.array
startTime = datetime.now()

with open(str(json_dir) + "/var-attrs.json") as f:
    var_attrs = json.load(f)

with open(str(json_dir) + "/case-attrs.json") as f:
    case_attrs = json.load(f)

case_study = "high_level"
model = "gfs"
int_dir = "20190517T00"

# case_study = "sparks_lake"
# model = "gfs"
# int_dir = "20210625T00"


pathlist = sorted(
    Path(str(data_dir) + f"/{case_study}/{model}/{int_dir}").glob(f"*.grib2")
)

ds = open_data(pathlist, 5, model, "50kPa")

ds = ds.sel(longitude=slice(169, 351), latitude=slice(90, 0))
X, Y, Z = (ds.longitude - 180) * -1, ds.latitude, ds.gh.sel(isobaricInhPa=500) / 1000
X, Y = np.meshgrid(X, Y)


fig = plt.figure(figsize=(12, 6))
ax = Axes3D(fig, xlim=[-180, 0], ylim=[0, 90], zlim=[4, 6])
# ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1, 1, 0.5, 1]))


target_projection = ccrs.PlateCarree()

feature = cartopy.feature.NaturalEarthFeature("physical", "coastline", "110m")
geoms = feature.geometries()

geoms = [target_projection.project_geometry(geom, feature.crs) for geom in geoms]

paths = list(itertools.chain.from_iterable(geos_to_path(geom) for geom in geoms))


segments = []
for path in paths:
    vertices = [vertex for vertex, _ in path.iter_segments()]
    vertices = np.asarray(vertices)
    if (vertices.max(axis=0)[0] > X.max()) or (vertices.min(axis=0)[1] < Y.min()):
        pass
    else:
        segments.append(vertices)

lc = LineCollection(segments, color="black")

ax.add_collection3d(lc, zs=4)
#
# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap="coolwarm", linewidth=0, antialiased=False)

# ax.zaxis.set_major_locator(LinearLocator(10))
# # A StrMethodFormatter is used automatically
# ax.zaxis.set_major_formatter('{x:.02f}')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Height")


plt.show()
# %%
