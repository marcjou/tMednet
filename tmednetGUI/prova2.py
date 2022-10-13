import os

os.environ['PROJ_LIB'] = '/home/marcjou/anaconda3/envs/tMednet/share/proj/'

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
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


def map_temperature(lat, lon, realtime, asst):
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent([-9.5, 37., 28., 50.], crs=ccrs.PlateCarree())
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.LAND)
    ax.coastlines(resolution='10m')
    ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)
    lons, lats = np.meshgrid(lon, lat)
    filenames = []
    print('bbefore levels')
    levels = np.arange(math.trunc(float(np.amin(asst)) - 273.15), math.trunc(float(np.amax(asst)) - 273.15) + 1, 1)
    print('after levels')
    # mhw.detect(ordtime, temp)

    for i in range(0, asst.shape[0]):
        temp = ax.contourf(lons, lats, asst[i, :, :] - 273.15, transform=ccrs.PlateCarree(), cmap='RdYlBu_r')
        if i == 0:
            cb = plt.colorbar(temp, location="bottom", ticks=levels)
        plt.title(realtime[i])
        plt.show()
        print('hey')
        plt.savefig('../src/output_images/image_' + str(i) + '.png')
        print('hoy')
        filenames.append('../src/output_images/image_' + str(i) + '.png')

    # build gif
    with imageio.get_writer('mygif3.gif', mode='I', duration=0.7) as writer:
        for filename in filenames:
            image = imageio.v3.imread(filename)
            writer.append_data(image)
    import os
    # Remove files
    for filename in set(filenames):
        os.remove(filename)


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
asst = nc.variables['analysed_sst'][:]






map_temperature(lat, lon, realtime, asst)

print('hola')
