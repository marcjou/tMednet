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
from datetime import datetime


from scipy import io, interpolate
mat = io.loadmat('../src/mhwclim_1982-2011_L4REP_MED.mat')

# TODO keep on working on implementing NAT clim to our code. Needed to interpolate his resolution with ours, check how to do it, maybe solved, took too long


nc = NetCDFFile('/home/marcjou/Escritorio/Projects/Sat_Data/reduced_20220627.nc')
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
time = nc.variables['time'][:]
tunits = nc.variables['time'].units
tcal = nc.variables['time'].calendar
time = num2date(time, tunits, tcal)
realtime = [i.strftime('%Y-%m-%d') for i in time]
dtime = [datetime.strptime(i, '%Y-%m-%d') for i in realtime]
ordtime = [x.toordinal() for x in dtime]
sst = nc.variables['analysed_sst'][:]
sst_day1 = sst[0, :, :]
clim = {}

clim['seas'] = mat['mhwclim']['mean'][0,0]
clim['thresh'] = mat['mhwclim']['m90'][0,0]
clim['seas'] = np.swapaxes(clim['seas'], 0, 1)
clim['thresh'] = np.swapaxes(clim['thresh'], 0, 1)
clim['missing'] = np.isnan(clim['seas'])

clim_lat = mat['mhwclim']['lat'][0,0][:, 0]
clim_lon = mat['mhwclim']['lon'][0,0][0, :]

# TODO here I talk about interpolation

li = []
for i in range(0, len(sst[:,0,0])):
    interp = interpolate.interp2d(lon, lat, sst[i, :, :], kind='cubic') # Interpolation from the 0.01 resolution to 0.05
    new_sst = interp(clim_lon, clim_lat)
    li.append(new_sst)
inter_sst = np.stack(li)
inter_sst = np.ma.masked_where(inter_sst <= -32767., inter_sst) - 273.15

point_clim = {}

for i in range(0,len(clim_lat)):
    for j in range(0,len(clim_lon)):
        if np.ma.is_masked(inter_sst[0,i,j]):
            pass
        else:
            sstt = inter_sst[:,i,j].tolist()
            point_clim['seas'] = clim['seas'][i, j, :]
            point_clim['thresh'] = clim['thresh'][i, j, :]
            point_clim['missing'] = clim['missing'][i, j, :]
            mhws = mhw.detect(ordtime, sstt, previousClimatology=point_clim)

mhw = mhw.detect(ordtime, new_sst, previousClimatology=clim)

# Desmontar el 29 de Febrero, el dia numero 60 del año (orden 59 en array)
clim[:,:,59]

print('hola')
