import os
import time
import math
import imageio
import calendar
import numpy as np
import xarray as xr
import pandas as pd
from sys import _getframe
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
from datetime import datetime, date
from typing import Literal, get_args, get_origin

os.environ['PROJ_LIB'] = '/home/marcjou/anaconda3/envs/tMednet/share/proj/'


class MHWMapper:
    """
    Creates a MHWMapper object which is a netcdf file open with xarray. This object has methods to create
    different maps regarding the MHW

    ...

    Attributes
    ----------
    ds : xarray DatArray
        array that contains all the netcdf data
    MHW : xarray DataArray
        array with the intensity of the MHW of a whole year of operation
    MHW_days : xarray DataArray
        array with the duration of the MHW of a whole year of operation
    ds_dtime : xarray DataArray
        array with the dates of the year of operation in datetime64
    lat : xarray DataArray
        array containing the latitude coordinates
    lon : xarray DataArray
        array containing the longitude coordinates
    ds_time : xarray DataArray
        array that contains the dates of the period being plotted
    ds_MHW_sliced : xarray DataArray
        array with the intensity of the MHW of the period being plotted
    ds_MHW_days_sliced : xarray DataArray
        array with the duration of the MHW of the period being plotted

    Methods
    -------

=======
    map_temperature(mode)
        saves a gif of the selected mode to be mapped


    Version: 02/2023, MJB: Documentation
    """

    _MODES = ['intensity', 'duration']

    def __init__(self, dataset_path, start_period=str(date.today().year) + '-06-01',
                 end_period=str(date.today().year) + '-06-30'):
        """
        Parameters
        ----------
        dataset_path : str
            complete path to the netcdf file to be open
        start_period: str, optional
            date in yyyy-mm-dd format that marks the start of the period to be plotted
            (default is the first of July of the current year)
        end_period: str, optional
            date in yyyy-mm-dd format that marks the end of the period to be plotted
            (default is the thirtieth of July of the current year)
        """
        # Set up the Netcdf satellite data using the xarray library
        with xr.open_dataset(dataset_path) as self.ds:
            self.MHW = self.ds.MHW
            self.MHW_days = self.ds.MHW_days
            self.ds_dtime = self.ds.time
            self.lat = self.ds.lat
            self.lon = self.ds.lon

        # Get the period you want to plot
        self.__set_sliced_ds(start_period, end_period)

    def __str__(self):
        return "<MHWMapper object>"

    def __set_sliced_ds(self, start_period, end_period):
        # Sets the dataset of the given period
        start_time = pd.to_datetime(start_period)
        try:
            end_time = pd.to_datetime(end_period)
            self.ds_dtime.loc[end_time]  # TODO change this to check if end_time exists in the ds
        except:
            end_time = self.ds_dtime[-1]
        self.ds_time = self.ds_dtime.loc[start_time:end_time].dt.strftime('%Y-%m-%d')
        self.ds_MHW_sliced = self.MHW.sel(time=slice(start_time, end_time))
        self.ds_MHW_days_sliced = self.MHW_days.sel(time=slice(start_time, end_time))

    @staticmethod
    def ax_setter():
        """
        Creates the axes where the map will be plotted selecting the coordinates to properly represent
        the Mediterranean sea and plots and colors the land and sea.

        Returns
        -------
        ax : Axes matplotlib
            the axes in which the data will be plotted
        """
        ax = plt.axes(projection=ccrs.Mercator())
        ax.set_extent([-9.5, 37., 28., 50.], crs=ccrs.PlateCarree())
        ax.add_feature(cf.OCEAN)
        ax.add_feature(cf.LAND)
        ax.coastlines(resolution='10m')
        ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)
        return ax

    @staticmethod
    def __enforce_literals(function):
        # Enforces that the correct options are selected on a given function
        kwargs = _getframe(1).f_locals
        for name, type_ in function.__annotations__.items():
            value = kwargs.get(name)
            options = get_args(type_)
            if get_origin(type_) is Literal and name in kwargs and value not in options:
                raise AssertionError(f"'{value}' is not in {options} for '{name}'")

    def __get_duration(self, lats, lons):
        # Returns the duration array on a way that each day shows the cumulative duration
        # TODO muy ineficiente, buscar la manera de comprobar si hay un hueco de dos dias
        #  o menos entre datos o si empieza el mes con datos del anterior de manera más eficiente.
        #  Ahora 16s por loop de lat, 127 loops igual a 33min de procesado
        raw_duration = self.ds_MHW_days_sliced
        proc_duration = raw_duration.copy()
        for i in range(0, len(lats)):
            start = time.time()
            for j in range(0, len(lons)):
                counter = 0
                counter2 = 0
                index = 0
                for n in range(0, len(raw_duration)):
                    if n == 0:
                        if raw_duration[n, i, j].isnull() == False:
                            counter = 1 + counter
                            proc_duration[n, i, j] = counter
                            index = n
                    elif counter > 0:
                        if n <= len(raw_duration) - 3:
                            if (raw_duration[n - 1, i, j].isnull() == False or raw_duration[
                                n - 2, i, j].isnull() == False) and (
                                    raw_duration[n + 1, i, j].isnull() == False or raw_duration[
                                n + 2, i, j].isnull() == False):
                                counter = 1 + counter
                                proc_duration[n, i, j] = counter
                                index = n
                            else:
                                # raw_duration[0:index - 2, i, j] = range(1, counter - 1)
                                counter = 0
                                index = 0
                    elif n > 0 and counter == 0:
                        if index == 0:
                            oldindex = n
                        if raw_duration[n, i, j].isnull() == False:
                            counter2 = 1 + counter2
                            proc_duration[n, i, j] = counter2
                            index = n
                        if n <= len(raw_duration) - 3:
                            if (raw_duration[n - 1, i, j].isnull() == False or raw_duration[
                                n - 2, i, j].isnull() == False) and (
                                    raw_duration[n + 1, i, j].isnull() == False or raw_duration[
                                n + 2, i, j].isnull() == False):
                                counter2 = 1 + counter2
                                proc_duration[n, i, j] = counter2
                                index = n
                            else:
                                # raw_duration[oldindex:index - 2, i, j] = range(1, counter2 - 1)
                                counter2 = 0
                                index = 0

            end = time.time()
            timu = end - start
            print('Time for looping over a single lat: ' + str(timu))
        return proc_duration

    def __create_image_by_type(self, lons, lats, mode, filenames):
        # Plots the given map and returns the filenames of the temporary images
        # created to be used for the gif
        start = time.time()
        if mode == 'temperature':
            ds = self.ds_asst_interpolated
            levels = np.arange(math.trunc(float(np.nanquantile(np.ma.filled(ds, np.nan), 0.01))),
                               math.trunc(float(np.nanquantile(np.ma.filled(ds, np.nan), 0.99))) + 1, 1)
            cmap = 'RdYlBu_r'
            ylabel = 'Temperature (ºC)'
        elif mode == 'duration':
            ds = self.__get_duration(lats, lons)
            levels = np.arange(0, 31, 5)
            cmap = 'Purples'
            ylabel = 'Duration (Nº days)'
        elif mode == 'intensity':
            ds = self.ds_MHW_sliced
            levels = np.arange(0, 10, 1)
            cmap = 'gist_heat_r'
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
            # if i == 0:
            cb = plt.colorbar(temp, location="bottom", ticks=levels, label=ylabel)
            plt.title(str(self.ds_time[i].values))
            # plt.show()
            print('hey')
            plt.savefig('../src/output_images/image_' + str(i) + '.png')
            print('hoy')
            filenames.append('../src/output_images/image_' + str(i) + '.png')
            ax.remove()
        return filenames

    def map_temperature(self, mode: _MODES = 'intensity'):
        """
        Given the kind of map that wants to be plotted starts the methods to plot them and creates and saves
        a gif containing the given period of operation.

        Parameters
        ----------
        mode : str
            the type of map that needs to be plotted. The current options are: 'intensity' and 'duration'
        """
        self.__enforce_literals(self.map_temperature)
        lons, lats = self.lon, self.lat
        filenames = []
        filenames = self.__create_image_by_type(lons, lats, mode, filenames)
        dt = datetime.strptime(self.ds_time.values[0], '%Y-%m-%d')
        year = dt.year
        month = calendar.month_name[dt.month]
        # build gif
        with imageio.get_writer('../src/output_images/' + str(mode) + '_' + month + '_' + str(year) + '.gif', mode='I',
                                duration=0.7) as writer:
            for filename in filenames:
                image = imageio.v3.imread(filename)
                writer.append_data(image)
        import os
        # Remove files
        for filename in set(filenames):
            os.remove(filename)
