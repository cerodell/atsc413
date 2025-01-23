#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import cdsapi
import numpy as np
import pandas as pd
from datetime import datetime

from context import data_dir


c = cdsapi.Client()
save_dir = str(data_dir) + "/era5/"


# date_range = pd.date_range("2013-02-12", "2019-12-27")
date_range = pd.date_range("2025-01-07", "2025-01-08")
for date in date_range:
    startTime = datetime.now()
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "2m_dewpoint_temperature",
                "2m_temperature",
                "mean_sea_level_pressure",
                "100m_u_component_of_wind",
                "100m_v_component_of_wind",
            ],
            "year": date.strftime("%Y"),
            "month": date.strftime("%m"),
            "day": date.strftime("%d"),
            "time": [
                "00:00",
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
        },
        save_dir + f'era5-{date.strftime("%Y%m%d00")}.nc',
    )

    print(
        f'downloaded era5-{date.strftime("%Y%m%d00")}.nc in {datetime.now() - startTime}'
    )


# save_dir = "/Volumes/WFRT-Data02/era5/"
# file_name = "precip"
# # level = 'pressure'
# # get_data =  {
# #             'variable': 'geopotential',
# #             'pressure_level': '500'
# #             }

# level = "single"
# get_data = {
#     "variable": "total_precipitation",
#     # "variable": "mean_sea_level_pressure",
#     # "variable": "2m_temperature",
# }


# year = [
#     "1991",
#     "1992",
#     "1993",
#     "1994",
#     "1995",
#     "1996",
#     "1997",
#     "1998",
#     "1999",
#     "2000",
#     "2001",
#     "2002",
#     "2003",
#     "2004",
#     "2005",
#     "2006",
#     "2007",
#     "2008",
#     "2009",
#     "2010",
#     "2011",
#     "2012",
#     "2013",
#     "2014",
#     "2015",
#     "2016",
#     "2017",
#     "2018",
#     "2019",
#     "2020",
#     "2021",
# ]

# config = {
#     "format": "netcdf",
#     "product_type": "monthly_averaged_reanalysis_by_hour_of_day",
#     "year": year,
#     "month": [
#         "01",
#         "02",
#         "03",
#         "04",
#         "05",
#         "06",
#         "07",
#         "08",
#         "09",
#         "10",
#         "11",
#         "12",
#     ],
#     "time": [
#         "00:00",
#         "01:00",
#         "02:00",
#         "03:00",
#         "04:00",
#         "05:00",
#         "06:00",
#         "07:00",
#         "08:00",
#         "09:00",
#         "10:00",
#         "11:00",
#         "12:00",
#         "13:00",
#         "14:00",
#         "15:00",
#         "16:00",
#         "17:00",
#         "18:00",
#         "19:00",
#         "20:00",
#         "21:00",
#         "22:00",
#         "23:00",
#     ],
#     # "area": [
#     #     90,
#     #     -180,
#     #     -10,
#     #     10,
#     # ],
# }


# config.update(get_data)

# c = cdsapi.Client()
# c.retrieve(
#     f"reanalysis-era5-{level}-levels-monthly-means",
#     config,
#     save_dir + f"era5-{file_name}-monthly-{year[0]}-{year[-1]}.nc",
# )
# print(f"wrote:  {save_dir}era5-{file_name}-monthly-{year[0]}-{year[-1]}.nc")


# # year = [
# #     "1991",
# #     "1992",
# #     "1993",
# #     "1994",
# #     "1995",
# #     "1996",
# #     "1997",
# #     "1998",
# #     "1999",
# # ]

# # year = [
# #     "2000",
# #     "2001",
# #     "2002",
# #     "2003",
# #     "2004",
# #     "2005",
# #     "2006",
# #     "2007",
# #     "2008",
# #     "2009",
# # ]

# # year = [
# #     "2010",
# #     "2011",
# #     "2012",
# #     "2013",
# #     "2014",
# #     "2015",
# #     "2016",
# #     "2017",
# #     "2018",
# #     "2019",
# #     "2020",
# #     "2021",
# # ]


# # c.retrieve(
# #     "reanalysis-era5-pressure-levels",
# #     {
# #         "product_type": "reanalysis",
# #         "format": "netcdf",
# #         "variable": "geopotential",
# #         "pressure_level": "500",
# #         "year": year,
# #         "month": [
# #             "01",
# #             "02",
# #             "03",
# #             "04",
# #             "05",
# #             "06",
# #             "07",
# #             "08",
# #             "09",
# #             "10",
# #             "11",
# #             "12",
# #         ],
# #         "day": [
# #             "01",
# #             "02",
# #             "03",
# #             "04",
# #             "05",
# #             "06",
# #             "07",
# #             "08",
# #             "09",
# #             "10",
# #             "11",
# #             "12",
# #             "13",
# #             "14",
# #             "15",
# #             "16",
# #             "17",
# #             "18",
# #             "19",
# #             "20",
# #             "21",
# #             "22",
# #             "23",
# #             "24",
# #             "25",
# #             "26",
# #             "27",
# #             "28",
# #             "29",
# #             "30",
# #             "31",
# #         ],
# #         "time": [
# #             "00:00",
# #             "01:00",
# #             "02:00",
# #             "03:00",
# #             "04:00",
# #             "05:00",
# #             "06:00",
# #             "07:00",
# #             "08:00",
# #             "09:00",
# #             "10:00",
# #             "11:00",
# #             "12:00",
# #             "13:00",
# #             "14:00",
# #             "15:00",
# #             "16:00",
# #             "17:00",
# #             "18:00",
# #             "19:00",
# #             "20:00",
# #             "21:00",
# #             "22:00",
# #             "23:00",
# #         ],
# #         "area": [
# #             90,
# #             -180,
# #             -10,
# #             10,
# #         ],
# #     },
# #     save_dir + f"era5-50kPa-{year[0]}-{year[-1]}.nc",
# # )
# # print(f"wrote:  {save_dir}era5-50kPa-{year[0]}-{year[-1]}.nc")
