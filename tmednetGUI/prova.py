import numpy as np
import pandas as pd
import time
from pandas import ExcelWriter
from scipy.interpolate import LinearNDInterpolator

import marineHeatWaves as mhw
import shapefile as shp
import matplotlib.pyplot as plt
from netCDF4 import Dataset as NetCDFFile
from netCDF4 import num2date
import seaborn as sns
from datetime import datetime


from scipy import io, interpolate

import os

os.environ['PROJ_LIB'] = '/home/marcjou/anaconda3/envs/tMednet/share/proj/'


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

# TODO comprobar porque el mapa sale todo blanco el fondo cuando no deberia
# This whole block here is the function able to create the map gif
def map_temperature(lat, lon, realtime, asst, type='temperature'):
    map = Basemap(projection='merc', llcrnrlon=-9.5, llcrnrlat=28., urcrnrlon=37., urcrnrlat=50., resolution='i')
    map.drawcoastlines(linewidth=0.5)
    map.drawcountries()
    map.drawlsmask(land_color='#adc6a9', ocean_color='#608abf')  # can use HTML names or codes for colors
    lons, lats = np.meshgrid(lon, lat)
    x, y = map(lons, lats)
    filenames = []
    if type == 'temperature':
        levels = np.arange(math.trunc(float(np.amin(asst)) - 273.15), math.trunc(float(np.amax(asst)) - 273.15) + 1, 1)
        cmap = 'RdYlBu_r'
        for i in range(0, asst.shape[0]):
            temp = map.contourf(x, y, asst[i, :, :] - 273.15, cmap=cmap)
            if i == 0:
                cb = map.colorbar(temp, "bottom", size="5%", pad="2%", ticks=levels)
            plt.title(realtime[i])
            print('hey')
            plt.savefig('../src/output_images/image_' + str(i) + '.png')
            print('hoy')
            filenames.append('../src/output_images/image_' + str(i) + '.png')
    else:
        levels = np.arange(5, 31, 1)
        cmap = 'Purples'
        for i in range(0, asst.shape[0]):
            temp = map.contourf(x, y, asst[i, :, :], cmap=cmap)
            if i == 0:
                cb = map.colorbar(temp, "bottom", size="5%", pad="2%", ticks=levels)
            plt.title(realtime[i])
            print('hey')
            plt.savefig('../src/output_images/image_' + str(i) + '.png')
            print('hoy')
            filenames.append('../src/output_images/image_' + str(i) + '.png')
    # mhw.detect(ordtime, temp)



    # build gif
    with imageio.get_writer('mygif3.gif', mode='I', duration=0.7) as writer:
        for filename in filenames:
            image = imageio.v2.imread(filename)
            writer.append_data(image)
    import os
    # Remove files
    for filename in set(filenames):
        os.remove(filename)




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
lat_grid = np.repeat(lat.reshape(len(lat), 1), repeats=len(lon), axis=1)
lon_grid = np.repeat(lon.reshape(1, len(lon)), repeats=len(lat), axis=0)
clim_lat_grid = np.repeat(clim_lat.reshape(len(clim_lat), 1), repeats=len(clim_lon), axis=1)
clim_lon_grid = np.repeat(clim_lon.reshape(1, len(clim_lon)), repeats=len(clim_lat), axis=0)

li = []
for i in range(0, len(sst[:,0,0])):
    coords = np.column_stack((lon_grid[~sst[i,:,:].mask], lat_grid[~sst[i,:,:].mask]))
    new_sst = interpolate.griddata(coords, sst[i,:,:][~sst[i,:,:].mask], (clim_lon_grid, clim_lat_grid), method='nearest') # Interpolation from the 0.01 resolution to 0.05
    li.append(new_sst)
inter_sst = np.stack(li)
inter_sst = inter_sst - 273.15

point_clim = {}

duration = inter_sst.copy()
duration[:,:,:] = 0

for i in range(0,len(clim_lat)):
    for j in range(0,len(clim_lon)):
        if np.ma.is_masked(inter_sst[0,i,j]):
            pass
        else:
            sstt = inter_sst[:,i,j].tolist()
            point_clim['seas'] = clim['seas'][i, j, :]
            point_clim['thresh'] = clim['thresh'][i, j, :]
            point_clim['missing'] = clim['missing'][i, j, :]
            print(str(i) + ' i y la j ' + str(j))
            mhws, bad = mhw.detect(np.asarray(ordtime), sstt, previousClimatology=point_clim)
            # Sets the duration of the MHW into an array to be plotted
            if mhws['time_start'] != []:
                start = mhws['index_start'][0]
                for n in range(0, mhws['duration'][0]):
                    duration[start + n, i, j]= n + 1

# For the map we use CLIM LAT AND LON and realtime
# For duration map we use duration

# TODO check that the duration array works, create a Intensity array and plot the mhw map
# TODO plot also th egraph that QUIM wants which is a line graph of the temperature over the years (anomaly like)
# TODO create the anomaly graphs

map_temperature(clim_lat, clim_lon, realtime, duration, type='duration')


print('hola')
