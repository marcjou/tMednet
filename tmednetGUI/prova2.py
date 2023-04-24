import os
import time
from scipy import io, interpolate

os.environ['PROJ_LIB'] = '/home/marcjou/anaconda3/envs/tMednet/share/proj/'

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import pandas as pd
import time
from pandas import ExcelWriter
import marineHeatWaves as mhw
import xarray as xr
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import math

from netCDF4 import Dataset as NetCDFFile
from netCDF4 import num2date
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import imageio
from datetime import datetime

import mhw_map_creator as mpc


def ax_setter():
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent([-9.5, 37., 28., 50.], crs=ccrs.PlateCarree())
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.LAND)
    ax.coastlines(resolution='10m')
    ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)
    return ax


def map_temperature(lat, lon, realtime, asst):
    lons, lats = np.meshgrid(lon, lat)
    filenames = []
    print('bbefore levels')
    start = time.time()
    levels = np.arange(math.trunc(float(asst.quantile(0.01)) - 273.15), math.trunc(float(asst.quantile(0.99)) - 273.15) + 1, 1)
    end = time.time()
    timu = end - start
    print('Time for creating levels: ' + str(timu))
    print('after levels')
    # mhw.detect(ordtime, temp)
    ax = ax_setter()

    for i in range(0, asst.shape[0]):

        print('Loop i: ' + str(i))
        start = time.time()
        temp = ax.contourf(lons, lats, asst[i, :, :] - 273.15, levels=levels, transform=ccrs.PlateCarree(), cmap='RdYlBu_r')
        end = time.time()
        timu = end - start
        print('Time to create temp: ' + str(timu))
        if i == 0:
            cb = plt.colorbar(temp, location="bottom", ticks=levels)
        plt.title(str(realtime[i].values))
        # plt.show()
        print('hey')
        plt.savefig('../src/output_images/image_' + str(i) + '.png')
        print('hoy')
        filenames.append('../src/output_images/image_' + str(i) + '.png')
        #ax.remove()

    # build gif
    with imageio.get_writer('mygif3.gif', mode='I', duration=0.7) as writer:
        for filename in filenames:
            image = imageio.v3.imread(filename)
            writer.append_data(image)
    import os
    # Remove files
    for filename in set(filenames):
        os.remove(filename)


def mask_and_interpolate(ds_asst_sliced, lon_grid, lat_grid, clim_lon_grid, clim_lat_grid):
    # Mask the NaN values
    start = time.time()
    ds_asst_masked = ds_asst_sliced.to_masked_array()
    end = time.time()
    timu = end - start
    print('time for masking ds: ' + str(timu))

    # Here is where the intepolation takes effect
    start = time.time()
    li = []
    for i in range(0, len(ds_asst_sliced[:, 0, 0])):
        coords = np.column_stack((lon_grid[~ds_asst_masked[i, :, :].mask], lat_grid[~ds_asst_masked[i, :, :].mask]))
        new_sst = interpolate.griddata(coords, ds_asst_masked[i, :, :][~ds_asst_masked[i, :, :].mask],
                                       (clim_lon_grid, clim_lat_grid),
                                       method='nearest')  # Interpolation from the 0.01 resolution to 0.05
        li.append(new_sst)
    end = time.time()
    timu = end - start
    print('time for interpolating ds: ' + str(timu))
    inter_sst = np.stack(li)
    inter_sst = inter_sst - 273.15

    return inter_sst

'''
start = time.time()
nc = NetCDFFile('/home/marcjou/Escritorio/Projects/Sat_Data/reduced_20220627.nc')
end = time.time()
timu = end - start
print('time for nc: ' + str(timu))
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
times = nc.variables['time'][:]
tunits = nc.variables['time'].units
tcal = nc.variables['time'].calendar
times = num2date(times, tunits, tcal)
realtime = [i.strftime('%Y-%m-%d') for i in times]
dtime = [datetime.strptime(i, '%Y-%m-%d') for i in realtime]
ordtime = [x.toordinal() for x in dtime]
start = time.time()
asst = nc.variables['analysed_sst'][:]
end = time.time()
timu = end - start
print(' Time for nc: ' + str(timu))
'''


'''
# Set the matlab dictionary using the climatology from Nat
mat = io.loadmat('../src/mhwclim_1982-2011_L4REP_MED.mat')
clim = {}
clim['seas'] = mat['mhwclim']['mean'][0,0]
clim['thresh'] = mat['mhwclim']['m90'][0,0]
clim['seas'] = np.swapaxes(clim['seas'], 0, 1)
clim['thresh'] = np.swapaxes(clim['thresh'], 0, 1)
clim['missing'] = np.isnan(clim['seas'])
clim_lat = mat['mhwclim']['lat'][0,0][:, 0]
clim_lon = mat['mhwclim']['lon'][0,0][0, :]

# Set up the Netcdf satellite data using the xarray library
start = time.time()
with xr.open_dataset('/home/marcjou/Escritorio/Projects/Sat_Data/reduced_20220627.nc') as ds:
    variables = ds.variables
end = time.time()
timu = end - start
print('time for opening ds: ' + str(timu))
start = time.time()
ds_asst = ds.analysed_sst
ds_lat = ds.lat
ds_lon = ds.lon
ds_dtime = ds.time
ordtime = [pd.to_datetime(x).toordinal() for x in ds.time.values]

# Get the period you want to plot
start_time = pd.to_datetime('2022-06-01')
try:
    end_time = pd.to_datetime('2022-06-30')
    ds_dtime.loc[end_time]
except:
    end_time = ds_dtime[-1].values
ds_time = ds_dtime.loc[start_time:end_time].dt.strftime('%Y-%m-%d')
ds_asst_sliced = ds_asst.sel(time=slice(start_time, end_time))
end = time.time()
timu = end - start
print('time for storing the variables ds: ' + str(timu))

# Interpolate the satellite data with Nat's data
lat_grid = np.repeat(ds_lat.values.reshape(len(ds_lat), 1), repeats=len(ds_lon), axis=1)
lon_grid = np.repeat(ds_lon.values.reshape(1, len(ds_lon)), repeats=len(ds_lat), axis=0)
clim_lat_grid = np.repeat(clim_lat.reshape(len(clim_lat), 1), repeats=len(clim_lon), axis=1)
clim_lon_grid = np.repeat(clim_lon.reshape(1, len(clim_lon)), repeats=len(clim_lat), axis=0)


inter_sst = mask_and_interpolate(ds_asst_sliced, lon_grid, lat_grid, clim_lon_grid, clim_lat_grid)

point_clim = {}

duration = inter_sst.copy()
duration[:,:,:] = 0
start2 = time.time()
for i in range(0,len(clim_lat)):
    print('Estamos en la i: ' + i)
    for j in range(0,len(clim_lon)):
        if np.ma.is_masked(inter_sst[0,i,j]):
            pass
        else:
            sstt = inter_sst[:,i,j].tolist()
            point_clim['seas'] = clim['seas'][i, j, :]
            point_clim['thresh'] = clim['thresh'][i, j, :]
            point_clim['missing'] = clim['missing'][i, j, :]
            mhws, bad = mhw.detect(np.asarray(ordtime), sstt, previousClimatology=point_clim)
            # Sets the duration of the MHW into an array to be plotted
            if mhws['time_start'] != []:
                start = mhws['index_start'][0]
                for n in range(0, mhws['duration'][0]):
                    duration[start + n, i, j]= n + 1
end2 = time.time()
timu = end2 - start2
print('time for creating the duration: ' + str(timu))

map_temperature(ds_lat, ds_lon, ds_time, ds_asst_sliced)

'''

import mhw_mapper as mp
df_map = mp.MHWMapper('/mnt/MHW/2023_MHW.nc', start_period='2023-04-01', end_period='2023-04-20')
df_map.map_temperature('intensity')
print('hola')
