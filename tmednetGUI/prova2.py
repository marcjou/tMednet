import os
import time

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






map_temperature(ds_lat, ds_lon, ds_time, ds_asst_sliced)

print('hola')
