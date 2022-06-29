import numpy as np
import pandas as pd
import time
from pandas import ExcelWriter
from scipy.interpolate import LinearNDInterpolator

import marineHeatWaves as mhw
import xarray as xr
import shapefile as shp
import matplotlib.pyplot as plt
from netCDF4 import Dataset as NetCDFFile
from netCDF4 import num2date
import seaborn as sns


from scipy import io
mat = io.loadmat('../src/mhwclim_1982-2011_L4REP_MED.mat')

# TODO keep on working on implementing NAT clim to our code. Needed to interpolate his resolution with ours, check how to do it, maybe solved, took too long


nc = NetCDFFile('../src/SST_MED_SST_L4_NRT_OBSERVATIONS_010_004_c_V2_1656500346190.nc')
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
sst = nc.variables['analysed_sst'][:]
sst_day1 = sst[0, :, :]
clim = {}

clim['seas'] = mat['mhwclim']['mean'][0,0]
clim['thresh'] = mat['mhwclim']['m90'][0,0]


clim_lat = mat['mhwclim']['lat'][0,0][:, 0]
clim_lon = mat['mhwclim']['lon'][0,0][0, :]

clim_lons, clim_lats = np.meshgrid(clim_lon, clim_lat)  # 2D grid for interpolation

# TODO here I talk about interpolation

interp = LinearNDInterpolator(list(zip(lon, lat)), sst_day1)

final_interp = interp(clim_lons, clim_lats)

# Desmontar el 29 de Febrero, el dia numero 60 del año (orden 59 en array)
clim[:,:,59]

print('hola')
