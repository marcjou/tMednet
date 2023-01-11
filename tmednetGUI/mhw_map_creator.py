import os
import time
import math
import imageio
import numpy as np
import xarray as xr
import pandas as pd
import seaborn as sns
import shapefile as shp
import cartopy.crs as ccrs
from netCDF4 import num2date
import cartopy.feature as cf
from datetime import datetime, date
import marineHeatWaves as mhw
from pandas import ExcelWriter
import matplotlib.pyplot as plt
from scipy import io, interpolate
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset as NetCDFFile

os.environ['PROJ_LIB'] = '/home/marcjou/anaconda3/envs/tMednet/share/proj/'

class MHWMapper:
    _mat = ''
    duration = None
    intensity = None

    def __init__(self, climatology_path, dataset_path, start_period=str(date.today().year)+'-06-01', end_period=str(date.today().year)+'-06-30'):
        # Set the matlab dictionary using the climatology from Nat
        self._mat = io.loadmat(climatology_path)
        self.__set_clim()

        # Set up the Netcdf satellite data using the xarray library
        with xr.open_dataset(dataset_path) as self.ds:
            self.variables = self.ds.variables
        self.__set_ds()

        # Get the period you want to plot
        self.__set_sliced_ds(start_period, end_period)

        # Interpolate the satellite data with Nat's data
        self.ds_asst_interpolated = self.__mask_and_interpolate()

    def __str__(self):
        return "<MHWMapper object>"

    def __set_clim(self):
        self.clim = {}
        self.clim['seas'] = self._mat['mhwclim']['mean'][0, 0]
        self.clim['thresh'] = self._mat['mhwclim']['m90'][0, 0]
        self.clim['seas'] = np.swapaxes(self.clim['seas'], 0, 1)
        self.clim['thresh'] = np.swapaxes(self.clim['thresh'], 0, 1)
        self.clim['missing'] = np.isnan(self.clim['seas'])
        self.clim_lat = self._mat['mhwclim']['lat'][0, 0][:, 0]
        self.clim_lon = self._mat['mhwclim']['lon'][0, 0][0, :]
        self.clim_seas_transposed = np.transpose(self.clim['seas'], (2, 0, 1))
        return self.clim, self.clim_lat, self.clim_lon

    def __set_ds(self):
        self.ds_asst = self.ds.analysed_sst
        self.ds_lat = self.ds.lat
        self.ds_lon = self.ds.lon
        self.ds_dtime = self.ds.time
        self.ordtime = [pd.to_datetime(x).toordinal() for x in self.ds.time.values]

    def __set_sliced_ds(self, start_period, end_period):
        start_time = pd.to_datetime(start_period)
        start_year = pd.to_datetime(str(date.today().year)+'-01-01')
        start_index = (start_time - start_year).days - 1
        try:
            end_time = pd.to_datetime(end_period)
            end_index = (end_time - start_year).days
            self.ds_dtime.loc[end_time]  # TODO change this to check if end_time exists in the ds
        except:
            end_time = self.ds_dtime[-1].values
            end_index = (end_time - start_year).days
        self.clim_sliced = self.clim_seas_transposed[start_index:end_index, :, :]
        self.ds_time = self.ds_dtime.loc[start_time:end_time].dt.strftime('%Y-%m-%d')
        self.ds_asst_sliced = self.ds_asst.sel(time=slice(start_time, end_time))

    def __mask_and_interpolate(self):
        lat_grid = np.repeat(self.ds_lat.values.reshape(len(self.ds_lat), 1), repeats=len(self.ds_lon), axis=1)
        lon_grid = np.repeat(self.ds_lon.values.reshape(1, len(self.ds_lon)), repeats=len(self.ds_lat), axis=0)
        clim_lat_grid = np.repeat(self.clim_lat.reshape(len(self.clim_lat), 1), repeats=len(self.clim_lon), axis=1)
        clim_lon_grid = np.repeat(self.clim_lon.reshape(1, len(self.clim_lon)), repeats=len(self.clim_lat), axis=0)

        # Mask the NaN values
        ds_asst_masked = self.ds_asst_sliced.to_masked_array()

        # Here is where the intepolation takes effect
        li = []
        for i in range(0, len(self.ds_asst_sliced[:, 0, 0])):
            coords = np.column_stack((lon_grid[~ds_asst_masked[i, :, :].mask], lat_grid[~ds_asst_masked[i, :, :].mask]))
            new_sst = interpolate.griddata(coords, ds_asst_masked[i, :, :][~ds_asst_masked[i, :, :].mask],
                                           (clim_lon_grid, clim_lat_grid),
                                           method='nearest')  # Interpolation from the 0.01 resolution to 0.05
            li.append(new_sst)
        inter_sst = np.stack(li)
        inter_sst = inter_sst - 273.15
        masked_sst = np.ma.masked_where(~np.isfinite(self.clim_sliced), inter_sst)
        return masked_sst

    def get_duration(self):
        point_clim = {}
        self.duration = self.ds_asst_interpolated.copy()
        self.duration[:, :, :] = 0
        for i in range(0, len(self.clim_lat)):
            print('Estamos en la i: ' + str(i))
            for j in range(0, len(self.clim_lon)):
                if np.ma.is_masked(self.ds_asst_interpolated[0, i, j]):
                    pass
                else:
                    sstt = self.ds_asst_interpolated[:, i, j].tolist()
                    point_clim['seas'] = self.clim['seas'][i, j, :]
                    point_clim['thresh'] = self.clim['thresh'][i, j, :]
                    point_clim['missing'] = self.clim['missing'][i, j, :]
                    mhws, bad = mhw.detect(np.asarray(self.ordtime), sstt, previousClimatology=point_clim)
                    # Sets the duration of the MHW into an array to be plotted
                    if mhws['time_start'] != []:
                        #for m in range(0, len(mhws['index_start'])):
                        start = mhws['index_start'][0]
                        for n in range(0, mhws['duration'][0]):
                            self.duration[start + n, i, j] = n + 1

        return self.duration

    def get_intensity(self):
        point_clim = {}
        self.intensity = self.ds_asst_interpolated.copy()
        self.intensity[:, :, :] = 0
        for i in range(0, len(self.clim_lat)):
            print('Estamos en la i: ' + str(i)
                  )
            for j in range(0, len(self.clim_lon)):
                if np.ma.is_masked(self.ds_asst_interpolated[0, i, j]):
                    pass
                else:
                    sstt = self.ds_asst_interpolated[:, i, j].tolist()
                    point_clim['seas'] = self.clim['seas'][i, j, :]
                    point_clim['thresh'] = self.clim['thresh'][i, j, :]
                    point_clim['missing'] = self.clim['missing'][i, j, :]
                    mhws, bad = mhw.detect(np.asarray(self.ordtime), sstt, previousClimatology=point_clim)
                    # Sets the duration of the MHW into an array to be plotted
                    if mhws['time_start'] != []:
                        for m in range(0, len(mhws['index_start'])):
                            start = mhws['index_start'][m]
                            for n in range(0, mhws['duration'][m]):
                                self.intensity[start + n, i, j] = sstt[start + n] - point_clim['seas'][start + n]

        return self.intensity

    @staticmethod
    def ax_setter():
        ax = plt.axes(projection=ccrs.Mercator())
        ax.set_extent([-9.5, 37., 28., 50.], crs=ccrs.PlateCarree())
        ax.add_feature(cf.OCEAN)
        ax.add_feature(cf.LAND)
        ax.coastlines(resolution='10m')
        ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)
        return ax

    def __create_image_by_type(self, lons, lats, mode, filenames):
        start = time.time()
        if mode == 'temperature':
            ds = self.ds_asst_interpolated
            levels = np.arange(math.trunc(float(np.nanquantile(np.ma.filled(ds, np.nan), 0.01))),
                               math.trunc(float(np.nanquantile(np.ma.filled(ds, np.nan), 0.99))) + 1, 1)
            cmap = 'RdYlBu_r'
            ylabel = 'Temperature (ºC)'
        elif mode == 'duration':
            self.duration = self.get_duration()
            ds = np.ma.masked_where(self.duration == 0, self.duration)
            levels = np.arange(0, 31, 5)
            cmap = 'Purples'
            ylabel = 'Duration (Nº days)'
        elif mode == 'intensity':
            self.intensity = self.get_intensity()
            ds = np.ma.masked_where(self.intensity == 0, self.intensity)
            levels = np.arange(0, 10, 1)
            cmap = 'RdYlBu_r'
            ylabel = 'Max Intensity (ºC)'
        end = time.time()
        timu = end - start
        print('Time for creating levels: ' + str(timu))
        print('after levels')

        for i in range(0, ds.shape[0]):
            ax = self.ax_setter()
            print('Loop i: ' + str(i))
            start = time.time()
            temp = ax.contourf(lons, lats, ds[i, :, :], levels=levels, transform=ccrs.PlateCarree(),
                               cmap=cmap)
            end = time.time()
            timu = end - start
            print('Time to create temp: ' + str(timu))
            #if i == 0:
            cb = plt.colorbar(temp, location="bottom", ticks=levels, label=ylabel)
            plt.title(str(self.ds_time[i].values))
            # plt.show()
            print('hey')
            plt.savefig('../src/output_images/image_' + str(i) + '.png')
            print('hoy')
            filenames.append('../src/output_images/image_' + str(i) + '.png')
            ax.remove()
        return filenames

    def map_temperature(self, mode):
        lons, lats = np.meshgrid(self.clim_lon, self.clim_lat)
        filenames = []
        filenames = self.__create_image_by_type(lons, lats, mode, filenames)
        # build gif
        with imageio.get_writer('../src/output_images/' + str(mode) + '_June_VJan23gif.gif', mode='I', duration=0.7) as writer:
            for filename in filenames:
                image = imageio.v3.imread(filename)
                writer.append_data(image)
        import os
        # Remove files
        for filename in set(filenames):
            os.remove(filename)

