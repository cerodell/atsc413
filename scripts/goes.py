from goes2go import GOES
from goes2go.data import goes_nearesttime
from goes2go.rgb import normalize, TrueColor, NaturalColor

import matplotlib.pyplot as plt


# # Get an ABI Dataset
# G = GOES().latest()

# # Create RGB and plot
# plt.imshow(G.rgb.TrueColor())

from goes2go import GOES
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

# # Download and read a GOES ABI MCMIPC dataset
# G = GOES(satellite=16, product="ABI-L2-FDC").latest()

# # Make figure on Cartopy axes
# ax = plt.subplot(projection=G.rgb.crs )
# ax.imshow(G.rgb.FireTemperature(), **G.rgb.imshow_kwargs)
# ax.coastlines()

# g = goes_nearesttime("2021-01-01 18:00", satellite=16, product="ABI", domain="F")
# # Original TrueColor
# tc = TrueColor(g, night_IR=False)

# # Rick Kohrs's Natural Color
# nc = NaturalColor(g, night_IR=False)
# fig, (ax1, ax2) = plt.subplots(
#     1, 2, figsize=[20, 10], subplot_kw=dict(projection=g.rgb.crs)
# )

# # for ax in [ax1, ax2]:
# #     common_features(ax=ax, STATES=True)


# ax1.imshow(g.rgb.TrueColor(), **g.rgb.imshow_kwargs)
# ax1.set_title("True Color", color="w")
# ax1.axis("off")

# ax2.imshow(g.rgb.NaturalColor(), **g.rgb.imshow_kwargs)
# ax2.set_title("Natural Color", color="w")
# ax2.axis("off")

# plt.subplots_adjust(wspace=0.01)
# fig.set_facecolor("k")

# goes_ds = goes_nearesttime("2021-07-02", satellite=16, product="ABI-L2-FDCF", domain="F")


# proj_info = goes_ds['goes_imager_projection']
# lon_origin = proj_info.longitude_of_projection_origin
# H = proj_info.perspective_point_height+proj_info.semi_major_axis
# r_eq = proj_info.semi_major_axis
# r_pol = proj_info.semi_minor_axis

# lon_rad_1d = goes_ds.y.values
# lat_rad_1d = goes_ds.x.values

# # create meshgrid filled with radian angles
# lat_rad,lon_rad = np.meshgrid(lat_rad_1d,lon_rad_1d)

# # lat/lon calc routine from satellite radian angle vectors

# lambda_0 = (lon_origin*np.pi)/180.0

# a_var = np.power(np.sin(lat_rad),2.0) + (np.power(np.cos(lat_rad),2.0)*(np.power(np.cos(lon_rad),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(lon_rad),2.0))))
# b_var = -2.0*H*np.cos(lat_rad)*np.cos(lon_rad)
# c_var = (H**2.0)-(r_eq**2.0)

# r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)

# s_x = r_s*np.cos(lat_rad)*np.cos(lon_rad)
# s_y = - r_s*np.sin(lat_rad)
# s_z = r_s*np.cos(lat_rad)*np.sin(lon_rad)

# lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
# lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)


# # print test coordinates
# print('{} N, {} W'.format(lat[318,1849],abs(lon[318,1849])))

# bbox = [np.min(lon),np.min(lat),np.max(lon),np.max(lat)] # set bounds for plotting

# ax = plt.subplot(projection=G.FOV.crs )
# ax.imshow(G['Power'])
# ax.coastlines()

# # Original TrueColor
# tc = TrueColor(g, night_IR=False)

# # Rick Kohrs's Natural Color
# nc = NaturalColor(g, night_IR=False)

# #%config InlineBackend.print_figure_kwargs = {'facecolor' : 'k'}
# # %config InlineBackend.print_figure_kwargs = {'facecolor' : 'none'}
# # %config InlineBackend.print_figure_kwargs = {'facecolor' : 'w'}
# fig = plt.figure(figsize=(14, 6))
# ax = fig.add_subplot(1, 1, 1)
# ax.imshow(g.rgb.NaturalColor(), **g.rgb.imshow_kwargs)
# ax.set_title("Natural Color", color="w")
# ax.axis("off")
# plt.subplots_adjust(wspace=0.01)
# fig.set_facecolor("k")

# fig, (ax1, ax2) = plt.subplots(
#     1, 2, figsize=[20, 10], subplot_kw=dict(projection=g.rgb.crs)
# )

# for ax in [ax1, ax2]:
#     common_features(ax=ax, STATES=True)


# ax1.imshow(g.rgb.TrueColor(), **g.rgb.imshow_kwargs)
# ax1.set_title("True Color", color="w")
# ax1.axis("off")

# ax2.imshow(g.rgb.NaturalColor(), **g.rgb.imshow_kwargs)
# ax2.set_title("Natural Color", color="w")
# ax2.axis("off")

# plt.subplots_adjust(wspace=0.01)
# fig.set_facecolor("k")

# plt.savefig("../docs/_static/True-vs-Natural_color", bbox_inches="tight")
