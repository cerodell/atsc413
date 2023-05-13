import context

import numpy as np
import pandas as pd
import xarray as xr

from context import data_dir


import matplotlib.pyplot as plt
import os.path

import tephi

# dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
# dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))


df = pd.read_csv(str(data_dir) + "/upperair/23March2011Sounding.csv")
df = df[:3500]

# dews = zip(dew_data.pressure, dew_data.dewpoint)
dews = zip(df["P (hPa)"].values, df["TD (degC)"].values)
temp = zip(df["P (hPa)"].values, df["T (degC)"].values)

# tpg = tephi.Tephigram()
# tpg.plot(dews)
# plt.show()


tpg = tephi.Tephigram()
profile = tpg.plot(dews)
df1 = df[::100]
barbs = zip(df1["FF (km/h)"], df1["DD (degN)"], df1["P (hPa)"])
profile.barbs(barbs)
profile = tpg.plot(temp)
plt.show()
