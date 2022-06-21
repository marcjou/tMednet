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

nc = NetCDFFile('../src/input_files/SST_MED_SST_L4_NRT_OBSERVATIONS_010_004_a_V2_1655810288836.nc')
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
map = Basemap(projection='merc',llcrnrlon=-9.5,llcrnrlat=28.,urcrnrlon=37.,urcrnrlat=50.,resolution='i')
map.drawcoastlines(linewidth=0.5)
map.drawcountries()
map.drawlsmask(land_color='#adc6a9', ocean_color='#608abf') # can use HTML names or codes for colors
lons, lats = np.meshgrid(lon, lat)
x, y = map(lons, lats)
filenames = []
levels = np.arange(math.trunc(float(np.amin(asst)) - 273.15), math.trunc(float(np.amax(asst)) - 273.15)+ 1, 1)

#mhw.detect(ordtime, temp)

for i in range(0, asst.shape[0]):
    temp = map.contourf(x,y,asst[i,:,:] - 273.15, cmap='RdYlBu_r')
    if i == 0:
        cb = map.colorbar(temp, "bottom", size="5%", pad="2%", ticks=levels)
    plt.title(realtime[i])
    print('hey')
    plt.savefig('../src/output_images/image_' + str(i) + '.png')
    print('hoy')
    filenames.append('../src/output_images/image_' + str(i) + '.png')


# build gif
with imageio.get_writer('mygif.gif', mode='I', duration=0.7) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)
import os
# Remove files
for filename in set(filenames):
    os.remove(filename)

print('hola')
