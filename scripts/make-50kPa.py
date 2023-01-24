import context
import salem
import cfgrib
import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import cartopy.crs as ccrs
import cartopy.util as cutil
import cartopy.feature as cfeature

from context import data_dir


kPa50_climo = salem.open_xr_dataset(str(data_dir) + "/50kPa-Climo.nc")
# ds = xr.open_dataset(
#     str(data_dir) + f"/nam_218_20190516_0000_000.grb2", engine="cfgrib",
#         backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName':'gh' }}
# ).sel(isobaricInhPa = 500)

ds = xr.open_dataset(
    str(data_dir) + f"/gfs_3_20190516_0000_000.grb2", engine="cfgrib",
        backend_kwargs={'filter_by_keys': {'typeOfLevel': 'isobaricInhPa', 'shortName':'gh' }}
).sel(isobaricInhPa = 500)
ds['longitude'] = np.arange(-180,180,1)

ds = ds.drop(['isobaricInhPa', 'step'])
ds = kPa50_climo.salem.transform(ds)


# Import data
# grib_data = cfgrib.open_datasets(str(data_dir) + f"/gfs_3_20190516_0000_000.grb2")
# for i in range(len(grib_data)):
#     print('----------')
#     print(i)
#     print(list(grib_data[i]))




lons, lats, vtimes = ds.longitude.values, ds.latitude.values, ds.valid_time.values
kPa50 = ds.gh.values/10


datacrs = ccrs.PlateCarree()
plotcrs = ccrs.NorthPolarStereo(central_longitude=-100.0)

# Make a grid of lat/lon values to use for plotting with Basemap.
# lons, lats = np.meshgrid(lon, lat)

fig = plt.figure(1, figsize=(10., 5.))
gs = gridspec.GridSpec(2, 1, height_ratios=[1, .02],
                       bottom=.07, top=.99, hspace=0.01, wspace=0.01)

ax = plt.subplot(gs[0], projection=plotcrs)
ax.set_title('50-kPa Geopotential Heights (m)', loc='left')
ax.set_title('VALID: {}'.format(vtimes), loc='right')

#   ax.set_extent([west long, east long, south lat, north lat])
ax.set_extent([-170, -10, 15, 75], ccrs.PlateCarree())
ax.coastlines('50m', edgecolor='black', linewidth=0.5)
ax.add_feature(cfeature.STATES, linewidth=0.5)

levels = np.arange(471, 603, 3)
cs = ax.contour(lons, lats, kPa50, levels, colors='k',
                linewidths=1.0, linestyles='solid', transform=datacrs)
plt.clabel(cs, fontsize=8, inline=1, inline_spacing=10, fmt='%i',
           rightside_up=True, use_clabeltext=True)

# clevsped250 = np.arange(50, 230, 20)
cmap = plt.cm.get_cmap('BuPu')
cf = ax.contourf(lons, lats, kPa50, levels, cmap=cmap, transform=datacrs)
cax = plt.subplot(gs[1])
cbar = plt.colorbar(cf, cax=cax, orientation='horizontal', extend='max', extendrect=True)

plt.show()





