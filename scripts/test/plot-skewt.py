import context

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, SkewT
from metpy.units import units

from context import data_dir, img_dir

import matplotlib.pyplot as plt
import os.path

import tephi

# dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
# dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))


# df1 = pd.read_csv(str(data_dir)+ "/windsond/2023-03-24_1242_1.sounding.csv", skiprows=1)


df = pd.read_csv(
    str(data_dir) + "/windsond/2023-03-24_1242_1.template.csv", skiprows=1, sep="\s{2,}"
)
df = df[:-20]
theta = df["Dew point (C)"].values
# create the first plot
fig, ax1 = plt.subplots()

# plot the first data series on the first axis
ax1.plot(x, y1, color="blue", label="Data 1")

# set the label for the first y-axis
ax1.set_ylabel("Data 1", color="blue")

# create the second axis and plot the second data series on it
ax2 = ax1.twinx()
ax2.plot(x, y2, color="red", label="Data 2")

# set the label for the second y-axis
ax2.set_ylabel("Data 2", color="red")

# add a legend to the plot
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

# show the plot
plt.show()

# df.to_csv(str(data_dir)+ "/windsond/sonde1.csv")
# p = df['Pressure (mb)'].values * units.hPa
# T = df['Temperature (C)'].values * units.degC
# Td = df['Dew point (C)'].values * units.degC
# wind_speed = df['Wind speed (m/s)'].values * 1.94384 * units.knots
# wind_dir = df['Wind direction (true deg)'].values * units.degrees
# u, v = mpcalc.wind_components(wind_speed, wind_dir)
# ds = mpcalc.parcel_profile_with_lcl_as_dataset(p, T, Td)
# # Plot the data using the data from the xarray Dataset including the parcel temperature with
# # the LCL level included
# skew.plot(ds.isobaric, ds.ambient_temperature, 'r', lw = 2, label = 'Sonde 1 T')
# skew.plot(ds.isobaric, ds.ambient_dew_point, 'g', lw = 2, label = 'Sonde 1 TD')
# skew.plot(ds.isobaric, ds.parcel_temperature.metpy.convert_units('degC'), 'black')
# # Plot the wind barbs from the original data
# skew.plot_barbs(p[::6], u[::6], v[::6])


# df = pd.read_csv(str(data_dir)+ "/windsond/2023-03-24_1259.template.csv", skiprows=1, sep='\s{2,}')
# df = df[:-20]
# df.to_csv(str(data_dir)+ "/windsond/sonde2.csv")
# p = df['Pressure (mb)'].values * units.hPa
# T = df['Temperature (C)'].values * units.degC
# Td = df['Dew point (C)'].values * units.degC
# wind_speed = df['Wind speed (m/s)'].values * 1.94384 * units.knots
# wind_dir = df['Wind direction (true deg)'].values * units.degrees
# u, v = mpcalc.wind_components(wind_speed, wind_dir)
# ds = mpcalc.parcel_profile_with_lcl_as_dataset(p, T, Td)
# # Plot the data using the data from the xarray Dataset including the parcel temperature with
# # the LCL level included
# skew.plot(ds.isobaric, ds.ambient_temperature, 'r', lw = 2, alpha = 0.5, label = 'Sonde 2 T')
# skew.plot(ds.isobaric, ds.ambient_dew_point, 'g', lw = 2, alpha = 0.5,  label = 'Sonde 2 TD')
# # skew.plot(ds.isobaric, ds.parcel_temperature.metpy.convert_units('degC'), 'black')
# # Plot the wind barbs from the original data
# skew.plot_barbs(p[::7], u[::7], v[::7])

# # Add the relevant special lines
# pressure = np.arange(1000, 499, -50) * units('hPa')
# mixing_ratio = np.array([0.1, 0.2, 0.4, 0.6, 1, 1.5, 2, 3, 4,
#                         6, 8, 10, 13, 16, 20, 25, 30, 36, 42]).reshape(-1, 1) * units('g/kg')

# skew.plot_dry_adiabats(t0=np.arange(233, 533, 10) * units.K, alpha=0.25,
#                        colors='orangered', linewidths=1)
# skew.plot_moist_adiabats(t0=np.arange(233, 400, 5) * units.K, alpha=0.25,
#                          colors='tab:green', linewidths=1)
# skew.plot_mixing_lines(pressure=pressure, mixing_ratio=mixing_ratio, linestyles='dotted',
#                        colors='dodgerblue', linewidths=1)
# skew.ax.set_ylim(1000, 200)
# skew.ax.set_xlim(-30, 20)

# # Set some better labels than the default
# skew.ax.set_xlabel('Temperature (\N{DEGREE CELSIUS})')
# skew.ax.set_ylabel('Pressure (hPa)')
# # Add some titles
# legend = plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, borderpad=1)

# plt.title('UBC Windsond', loc='left')
# plt.title('2023-03-24 1200 PDT', loc='right')
# plt.savefig(
#     str(img_dir) + f"/sounding/2023-03-241T12.png",
#     dpi=250,
#     bbox_inches="tight",
# )

# skew = SkewT()

# # Plot the data using normal plotting functions, in this case using
# # log scaling in Y, as dictated by the typical meteorological plot
# skew.plot(p, T, 'r', lw = 4)
# skew.plot(p, Td, 'g', lw = 4)
# skew.plot_barbs(p[::10], u[::10], v[::10])

# # Set some better labels than the default
# skew.ax.set_xlabel('Temperature (\N{DEGREE CELSIUS})')
# skew.ax.set_ylabel('Pressure (hPa)')

# # Add the relevant special lines
# skew.plot_dry_adiabats()
# skew.plot_moist_adiabats()
# skew.plot_mixing_lines()
# skew.ax.set_ylim(1000, 100)
# skew.ax.set_xlim(-50, 20)

# # Add the MetPy logo!
# fig = plt.gcf()
# add_metpy_logo(fig, 115, 100)


# df = df[:3500]

# # dews = zip(dew_data.pressure, dew_data.dewpoint)
# dews = zip(df['P (hPa)'].values, df['TD (degC)'].values)
# temp = zip(df['P (hPa)'].values, df['T (degC)'].values)

# # tpg = tephi.Tephigram()
# # tpg.plot(dews)
# # plt.show()


# tpg = tephi.Tephigram()
# profile = tpg.plot(dews)
# df1 = df[::100]
# barbs =  zip(df1['FF (km/h)'],df1['DD (degN)'],df1['P (hPa)'])
# profile.barbs(barbs)
# profile = tpg.plot(temp)
# plt.show()
