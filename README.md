
# ATSC 413 Forest-fire Weather and Climate

The ATSC413 repo downloads archived numerical weather prediction (NWP) model output and generates a sweep of forecast products. The forecast products will aid in teaching a fourth-year synoptic fire weather meteorology course at the University of British Columbia. Student will uses the forecat poridcts to create m



## Forecast Products

The repo currently creates forecast maps centered over a specified region.

Products include:
- 25kPa Geopotential Heights (dam) and Wind Speed (knots)
- 50kPa Geopotential Heights (dam) and Anomaly (m)
- 3-h Precip (mm), MSLP (hPa), 100-50kPa Thickness (dam)
- 70kPa Relative Humidity (%)
- 3-hr Precipitation (mm)
- 2m Relative Humidity (%)
- 2m Temperature (C)
- Wind Speed and Direction at varied heights
- Surface-based CAPE (J/kg)


## Data

NWP data is downloaded from the [Research Data Archive (RDA)](https://rda.ucar.edu/) manged by the [National Center for Atmospheric Research (NCAR)](https://ncar.ucar.edu/).

## How to use

The
To download nwp data and generate forecast products, one needs to add a
