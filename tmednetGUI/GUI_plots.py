import sys
import time
import matplotlib
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
import file_writer as fw
import excel_writer as ew
from datetime import datetime
import marineHeatWaves as mhw
import tkinter.font as tkFont
import surface_temperature as st
from PIL import Image, ImageTk
import file_manipulation as fm
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from tkinter import messagebox, Button
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class GUIPlot:
    """
    Creates an object containing all the information necessary to create the different plots that will
    be shown on the GUI.

    ...

    Attributes
    ----------
    counter : list
        List containing information about the type of plot that is being created
    index : list
        List containing the pointer to the selected file on the list box
    dm : DataManager Object
        Object containing the instance of the data loaded into the GUI
    savefilename : str
        Name under which the plot will be saved

    Methods
    -------
    plot_ts(self, mdata, files, index)
        Plots the selected time series from the list of loaded files
    plot_zoom(self, mdata, files, list, cut_data_manually, controller=False)
        Plots a zoomed version of the selected time series from the list of loaded files
    plot_all_zoom(self, mdata, list)
        Plots a zoom version of multiple selected time series from the list of loaded files
    plot_dif(self, mdata)
        Plots the difference between consecutive depths of all the loaded files
    plot_dif_filter1d(self, mdata)
        Plots the filtered difference between consecutive depths of all the loaded files
    plot_hovmoller(self, mdata)
        Creates a hovmoller plot with only the time series loaded
    plot_stratification(self, historical, year)
        Creates the stratification plot of a given dataset and year
    plot_annual_T_cycle(self, historical, year)
        Creates the annual T cycle plot of a given dataset and year
    plot_thresholds(self, historical, toolbar, consolescreen)
        Creates the thresholds plot of a given dataset
    clear_plots(self, clear_thresholds=True)
        Deletes all current plots and plot related attributes

    Version: 03/2023 MJB: Documentation
    """

    def __init__(self, f2, console, reportlogger, dm):
        """
        Parameters
        ----------
        f2 : tKinter Frame
            Frame of the GUI where the plots will be placed
        console: function
            Function able to write on the GUI console
        reportlogger : function
            Function able to write on the report screen on the GUI
        """
        self.__set_args(f2)
        self.counter = []
        self.index = []
        self.console_writer = console
        self.reportlogger = reportlogger
        self.dm = dm
        self.savefilename = ""
        self.__cb = ""

    def __str__(self):
        return "GUIPlot object"

    def __set_args(self, f2):
        # Starts and sets the attributes of the plot and defines the aspects of the figure
        self.__curtab = None
        self.__tabs = {}
        plt.rc('legend', fontsize='medium')
        self.fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)
        self.__plot = self.fig.add_subplot(111)
        self.__plot1 = self.fig.add_subplot(211)
        self.__plot2 = self.fig.add_subplot(212)
        plt.Axes.remove(self.__plot1)
        plt.Axes.remove(self.__plot2)
        plt.Axes.remove(self.__plot)
        self.__cbexists = False  # Control for the colorbar of the Hovmoller
        self.canvas = FigureCanvasTkAgg(self.fig, master=f2)
        self.canvas.draw()
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def plot_ts(self, mdata, files, index):
        """
        Plots the selected time series from the list of loaded files

        ...

        Parameters
        ----------
        mdata : list
            Contains all the information that is stored in the database files
        files:  list
            Contains the names of the files that are being plot
        index:  int
            If there are multiple files loaded, this parameter refers to the one being plot
        """
        # If there are subplots, deletes them before creating the plot anew
        if self.__plot1.axes:
            plt.Axes.remove(self.__plot1)
            plt.Axes.remove(self.__plot2)

        if self.counter[0] == "Hovmoller":
            self.clear_plots()
        elif self.counter[0] == 'Cycles':
            self.clear_plots()
        elif self.counter[0] == 'Thresholds':
            self.clear_plots()
        elif self.counter[0] == 'Filter':
            self.clear_plots()
        elif self.counter[0] == 'Difference':
            self.clear_plots()

        masked_ending_temperatures = np.ma.masked_where(np.array(mdata[index]['df']['Temp']) == 999,
                                                        np.array(mdata[index]['df']['Temp']))
        if self.__plot.axes:
            # self.__plot = self.fig.add_subplot(111)
            self.__plot.plot(mdata[index]['df'].index, masked_ending_temperatures,
                           '-', label=str(mdata[index]['depth']))
            self.__plot.set(ylabel='Temperature (DEG C)',
                          title='Multiple depths Site: ' + str(mdata[index]['region_name']))
        else:
            self.__plot = self.fig.add_subplot(111)
            self.__plot.plot(mdata[index]['df'].index, masked_ending_temperatures,
                           '-', label=str(mdata[index]['depth']))
            self.__plot.set(ylabel='Temperature (DEG C)',
                          title=files[index] + "\n" + 'Depth:' + str(
                              mdata[index]['depth']) + " - Site: " + str(
                              mdata[index]['region_name']))

        self.__plot.legend(title='Depth (m)')
        # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_zoom(self, mdata, files, list, cut_data_manually, controller=False):
        """
        Plots a zoomed section of the beginning and ending of a selected
        time series from the list of loaded files

        ...

        Parameters
        ----------
        mdata : list
            Contains all the information that is stored in the database files
        files:  list
            Contains the names of the files that are being plot
        list:  tkinter Listbox
            Object that contains the list of loaded files
        cut_data_manually: function
            Allows to remove from mdata the points selected on the plot by the user
        """
        self.clear_plots()
        index = int(list.curselection()[0])
        time_series, temperatures, indexes, start_index, valid_start, valid_end = self.dm.zoom_data(mdata[index])

        self.counter.append(index)
        self.counter.append('Zoom')

        # Creates the subplots and deletes the old plot
        if not self.__plot1.axes:
            self.__plot1 = self.fig.add_subplot(211)
            self.__plot2 = self.fig.add_subplot(212)

        masked_temperatures = np.ma.masked_where(np.array(mdata[index]['df']['Temp']) == 999,
                                                 np.array(mdata[index]['df']['Temp']))

        self.__plot1.plot(time_series[0][int(start_index):], masked_temperatures[int(start_index) + int(valid_start):len(time_series[0]) + valid_start],
                        '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
        self.__plot1.legend()
        self.__plot1.plot(time_series[0][:int(start_index) + 1], masked_temperatures[valid_start:int(start_index) + 1 + int(valid_start)],
                        '-', color='red', marker='o', label=str(mdata[index]['depth']))

        self.__plot1.set(ylabel='Temperature (DEG C)',
                       title=files[index] + "\n" + 'Depth:' + str(
                           mdata[index]['depth']) + " - Region: " + str(
                           mdata[index]['region']))
        if indexes.size != 0:
            if indexes[0] + 1 == len(time_series[0]):
                self.__plot2.plot(time_series[1][:int(indexes[0])],
                                masked_temperatures[-len(time_series[1]):(int(indexes[0]) - len(time_series[1]))],
                                '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            else:
                self.__plot2.plot(time_series[1][:int(indexes[0] + 1)],
                                masked_temperatures[-len(time_series[1]):(int(indexes[0]) - len(time_series[1]) + 1)],
                                '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            self.__plot2.legend()
            # Plots in the same graph the last part which represents the errors in the data from removing the sensors
            self.__plot2.plot(time_series[1][int(indexes[0]):],
                            masked_temperatures[(int(indexes[0]) - len(time_series[1])):],
                            '-', color='red', marker='o', label=str(mdata[index]['depth']))
            self.__plot2.set(ylabel='Temperature (DEG C)',
                           title=files[index] + "\n" + 'Depth:' + str(
                               mdata[index]['depth']) + " - Region: " + str(
                               mdata[index]['region']))
        else:
            self.__plot2.plot(time_series[1],
                            masked_temperatures[-len(time_series[1]):],
                            '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            self.__plot2.legend()
            self.__plot2.set(ylabel='Temperature (DEG C)',
                           title=files[index] + "\n" + 'Depth:' + str(
                               mdata[index]['depth']) + " - Region: " + str(
                               mdata[index]['region']))
        # fig.set_size_inches(14.5, 10.5, forward=True)
        # Controls if we are accesing the event handler through a real click or it loops.
        if not controller:
            cid = self.fig.canvas.mpl_connect('button_press_event', lambda event: cut_data_manually(event, index))

        self.canvas.draw()
        self.console_writer('Plotting zoom of depth: ', 'action', mdata[0]['depth'])
        self.console_writer(' at site ', 'action', mdata[0]['region'], True)

    def plot_all_zoom(self, mdata, list):
        """
        Plots a zoomed section of the beginning and ending of multiple selected
        time series from the list of loaded files
        ...

        Parameters
        ----------
        mdata : list
            Contains all the information that is stored in the database files
        list:  tkinter Listbox
            Object that contains the list of loaded files
        """
        self.clear_plots()
        index = list.curselection()

        for item in index:
            self.counter.append(item)
        self.counter.append('Zoom')

        depths = ""
        # Creates the subplots and deletes the old plot
        if not self.__plot1.axes:
            self.__plot1 = self.fig.add_subplot(211)
            self.__plot2 = self.fig.add_subplot(212)

        for i in index:
            time_series, temperatures, _, bad, bad2, bad3 = self.dm.zoom_data(mdata[i])
            depths = depths + " " + str(mdata[i]['depth'])

            masked_temperatures = np.ma.masked_where(np.array(mdata[i]['df']['Temp']) == 999,
                                                     np.array(mdata[i]['df']['Temp']))

            masked_ending_temperatures = np.ma.masked_where(np.array(temperatures[1]) == 999,
                                                            np.array(temperatures[1]))
            self.__plot1.plot(time_series[0], masked_temperatures[:len(time_series[0])],
                            '-', label=str(mdata[i]['depth']))
            self.__plot1.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               mdata[i]['region']))
            self.__plot1.legend()

            self.__plot2.plot(time_series[1], masked_temperatures[-len(time_series[1]):],
                            '-', label=str(mdata[i]['depth']))
            self.__plot2.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               mdata[i]['region']))
            self.__plot2.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
        self.console_writer('Plotting zoom of depths: ', 'action', depths)
        self.console_writer(' at site ', 'action', mdata[0]['region'], True)

    def plot_dif(self):
        """
        Plots the difference between consecutive depths of all the loaded files
        ...

        Parameters
        ----------
        mdata : list
            Contains all the information that is stored in the database files
        """

        self.clear_plots()
        depths = ""
        try:
            dfdelta, _ = self.dm.temp_difference()
            self.counter.append('Difference')
            # Creates the subplots and deletes the old plot
            if self.__plot1.axes:
                plt.Axes.remove(self.__plot1)
                plt.Axes.remove(self.__plot2)

            self.__plot = self.fig.add_subplot(111)
            dfdelta.plot(ax=self.__plot)
            self.__plot.set(ylabel='Temperature (DEG C)',
                          title='Temperature differences')

            self.__plot.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
            self.console_writer('Plotting zoom of depths: ', 'action', depths)
            self.console_writer(' at site ', 'action', self.dm.mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_dif_filter1d(self):
        """
         Plots the filtered difference between consecutive depths of all the loaded files
         ...

         Parameters
         ----------
         mdata : list
             Contains all the information that is stored in the database files
         """

        self.clear_plots()
        depths = ""
        try:
            dfdelta = self.dm.apply_uniform_filter()
            self.counter.append("Filter")
            # Creates the subplots and deletes the old plot
            if self.__plot1.axes:
                plt.Axes.remove(self.__plot1)
                plt.Axes.remove(self.__plot2)
            for _, rows in dfdelta.iterrows():  # Checks if there is an erroneous value and if there is, logs it.
                for row in rows:
                    if float(row) <= -0.2:
                        self.console_writer('Attention, value under -0.2 threshold', 'warning')
                        self.reportlogger.append('Attention, value under -0.2 threshold')
                        break
                else:
                    continue
                break

            self.__plot = self.fig.add_subplot(111)
            dfdelta.plot(ax=self.__plot)
            self.__plot.set(ylabel='Temperature (DEG C)',
                          title='Temperature differences filtered')

            self.__plot.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
            self.console_writer('Plotting zoom of depths: ', 'action', depths)
            self.console_writer(' at site ', 'action', self.dm.mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_hovmoller(self, mdata):
        """
         Creates a hovmoller plot with only the time series loaded
         ...

         Parameters
         ----------
         mdata : list
             Contains all the information that is stored in the database files
         """
        try:
            self.clear_plots()
            self.counter.append("Hovmoller")
            df, depths, _ = self.dm.list_to_df()
            depths = np.array(depths)
            if self.__plot1.axes:
                plt.Axes.remove(self.__plot1)
                plt.Axes.remove(self.__plot2)
            self.__plot = self.fig.add_subplot(111)

            levels = np.arange(np.floor(np.nanmin(df.values)), np.ceil(np.nanmax(df.values)), 1)
            # df.resample(##) if we want to filter the results in a direct way
            # Draws a contourn line. Right now looks messy
            # ct = self.__plot.contour(df.index.to_pydatetime(), -depths, df.values.T, colors='black', linewidths=0.5)
            cf = self.__plot.contourf(df.index.to_pydatetime(), -depths, df.values.T, 256, extend='both', cmap='RdYlBu_r')

            self.__cb = plt.colorbar(cf, ax=self.__plot, label='Temperature (ºC)', ticks=levels)
            self.__cbexists = True
            self.__plot.set(ylabel='Depth (m)',
                          title='Stratification Site: ' + mdata[0]['region_name'])

            # Sets the X axis as the initials of the months
            locator = mdates.MonthLocator()
            self.__plot.xaxis.set_major_locator(locator)
            fmt = mdates.DateFormatter('%b')
            self.__plot.xaxis.set_major_formatter(fmt)
            # Sets the x axis on the top
            self.__plot.xaxis.tick_top()

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', mdata[0]['region'], True)
        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError:
            self.console_writer('Load more than a file for the Hovmoller Diagram', 'warning')

    def plot_stratification(self, historical, year):
        """
        Creates the stratification plot of a given dataset and year
        ...

        Parameters
        ----------
        historical : str
            Path of the dataset to be loaded
        year : str
            Year which wants to be plotted
        """
        df, hismintemp, hismaxtemp, bad = self.dm.historic_to_df(historical, year)
        try:
            self.clear_plots()
            self.counter.append("Stratification")
            depths = np.array(list(map(float, list(df.columns))))
            if self.__plot1.axes:
                plt.Axes.remove(self.__plot1)
                plt.Axes.remove(self.__plot2)
            self.__plot = self.fig.add_subplot(111)

            if depths[-1] < 40:
                self.__plot.set_ylim(0, -40)
                self.__plot.set_yticks(-np.insert(depths, [0, -1], [0, 40]))
            else:
                self.__plot.set_ylim(0, -depths[-1])
                self.__plot.set_yticks(-np.insert(depths, 0, 0))

            self.__plot.set_xlim(datetime.strptime('01/05/' + year + ' 00:00:00', '%d/%m/%Y %H:%M:%S'),
                               datetime.strptime('01/12/' + year + ' 00:00:00', '%d/%m/%Y %H:%M:%S'))
            # self.__plot.set_xlim(pd.to_datetime(df.index[0]), pd.to_datetime(df.index[-1]))

            # self.__plot.set_yticks(-np.arange(0, depths[-1]+1, 5))
            self.__plot.invert_yaxis()
            # levels = np.arange(np.floor(np.nanmin(df.values)), np.ceil(np.nanmax(df.values)), 1)
            #levels = np.arange(np.floor(hismintemp), np.ceil(hismaxtemp), 1)
            #levels2 = np.arange(np.floor(hismintemp), np.ceil(hismaxtemp), 0.1)

            # Checks the historic min and max values to use in the colourbar, if they are too outlandish
            # over 5 degrees of difference, it uses its own max and min for this year.
            # We use percentile 99% and 1% to decide the upper and lower levels and trim outlandish data
            dfcopy = df.copy()
            dfcopy.index = pd.to_datetime(dfcopy.index)
            dfcopy = dfcopy.loc[(dfcopy.index.month >= 5) & (dfcopy.index.month < 12)]
            # Quantile changes with the amount of data available, with less data is possible to have a higher outlier
            # We only take into account the quantile for all the years to make it correct.

            levels = np.arange(np.floor(hismintemp), hismaxtemp, 1)
            levels2 = np.arange(np.floor(hismintemp), hismaxtemp, 0.1)

            df_datetime = pd.to_datetime(df.index)
            old = df_datetime[0]
            index_cut = None
            df_cuts = []
            for i in df_datetime[1:]:
                new = i
                diff = new - old
                old = new
                if diff.days > 0:
                    index_old = 0
                    index_cut = df_datetime.get_loc(i)
                    df_cuts.append(df[index_old:index_cut])
                    index_old = index_cut
                    # df_second = df[index_cut:]
            # Checks how many depths the file has, if there is only one depth it creates a new one 1 meter above
            if len(depths) == 1:
                depths = np.insert(depths, 1, depths[0] + 2.5)
                depths = np.insert(depths, 0, depths[0] - 2.5)
                df.insert(0, str(depths[0]), df[str(depths[1])])
                df.insert(2, str(depths[2]), df[str(depths[1])])
            if index_cut:
                df_cuts.append(df[index_cut:])
                cf = []
                for i in range(0, len(df_cuts)):
                    cf.append(self.__plot.contourf(pd.to_datetime(df_cuts[i].index), -depths, df_cuts[i].values.T, 256,
                                                 extend='both',
                                                 cmap='RdYlBu_r', levels=levels2))
                self.__cb = plt.colorbar(cf[0], ax=self.__plot, label='Temperature (ºC)', ticks=levels)
            else:
                # Checks if there is a vertical gap bigger than 5 meters and if so instead of interpolating
                # Plots two different plots to keep the hole inbetween
                str_depths = [f'{x:g}' for x in depths]
                vertical_split = []
                for i in range(0, len(depths)):
                    if i < len(depths) - 1:
                        res = depths[i + 1] - depths[i]
                        if res > 10.:
                            vertical_split.append(i)
                if vertical_split:
                    old_index = 0
                    for i in vertical_split:
                        cf = self.__plot.contourf(df_datetime, -depths[old_index: i + 1],
                                                df.filter(items=str_depths[old_index:i + 1]).values.T, 256, extend='both',
                                                cmap='RdYlBu_r',
                                                levels=levels2)
                        old_index = i + 1
                    cf = self.__plot.contourf(df_datetime, -depths[old_index:],
                                            df.filter(items=str_depths[old_index:]).values.T, 256, extend='both',
                                            cmap='RdYlBu_r',
                                            levels=levels2)
                else:
                    cf = self.__plot.contourf(df_datetime, -depths, df.values.T, 256, extend='both', cmap='RdYlBu_r',
                                            levels=levels2)

                self.__cb = plt.colorbar(cf, ax=self.__plot, label='Temperature (ºC)', ticks=levels)
            self.__cbexists = True
            self.__plot.set(ylabel='Depth (m)',
                          title=historical.split('_')[4] + ' year ' + year)
            self.savefilename = historical.split('_')[3] + '_1_' + year + '_' + historical.split('_')[4]
            # Sets the X axis as the initials of the months
            locator = mdates.MonthLocator()
            self.__plot.xaxis.set_major_locator(locator)
            fmt = mdates.DateFormatter('%b')
            self.__plot.xaxis.set_major_formatter(fmt)
            # Sets the x axis on the top
            self.__plot.xaxis.tick_top()
            # Sets the ticks only for the whole depths, the ones from the file
            tick_depths = [-i for i in depths if i.is_integer()]
            self.__plot.set_yticks(tick_depths)

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', historical.split('_')[3], True)

        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError as e:
            self.console_writer('Load more than a file for the Hovmoller Diagram: ' + str(e), 'warning')

    def plot_annual_T_cycle(self, historical, year):
        """
        Creates the annual T cycle plot of a given dataset and year

        ...

        Parameters
        ----------
        historical : str
            Path of the dataset to be loaded
        year : str
            Year which wants to be plotted
        """
        self.clear_plots()
        self.counter.append("Cycles")

        histdf = pd.read_csv(historical, sep='\t')
        depths = histdf.columns[2:]
        # Drop the Nan date rows
        histdf.drop(histdf.loc[histdf['Date'].isnull()].index, inplace=True)
        histdf['day'] = pd.DatetimeIndex(histdf['Date'], dayfirst=True).day
        histdf['month'] = pd.DatetimeIndex(histdf['Date'], dayfirst=True).month
        histdf['day_month'] = histdf['day'].astype(str) + '-' + histdf['month'].astype(str)
        histdf['day_month'] = histdf['day_month'] + '-' + year
        # Check if the selected year is a leap year
        if pd.to_datetime(year).is_leap_year == False:
            histdf.drop(histdf['day_month'].loc[histdf['day_month'] == '29-2-' + str(year)].index, inplace=True)
        histdf['day_month'] = pd.DatetimeIndex(histdf['day_month'], dayfirst=True)

        orderedhist_df = histdf.groupby('day_month')[depths].mean()
        orderedhist_df.sort_index(inplace=True)

        year_df, hismintemp, hismaxtemp, minyear = self.dm.historic_to_df(historical, year, start_month='01', end_month='01')
        year_df.index = year_df.index.strftime('%Y-%m-%d %H:%M:%S')
        if '0' in year_df.columns:
            year_df.drop('0', axis=1, inplace=True)

        year_df = self.dm.running_average_special(year_df, running=360)
        # TODO discuss with Nat how many days for the running average of the climatology
        orderedhist_df = self.dm.running_average_special(orderedhist_df, running=30)
        orderedhist_df.index = pd.DatetimeIndex(orderedhist_df.index)

        # All this block serves only to transform the data from hourly to daily. It should be inside its own method
        daylist = []
        # Converts the index from timestamp to string
        daylist = []
        for time in year_df.index:
            if str(time) == 'nan':
                pass
            else:
                old = datetime.strftime(time, '%Y-%m-%d')
                new = datetime.strptime(old, '%Y-%m-%d')
            daylist.append(new)
        year_df['day'] = daylist

        newdf = None
        # Changed dfdelta here for year_df, if wrong, revert
        for depth in year_df.columns:
            if depth != 'day':
                if newdf is not None:
                    newdf = pd.merge(newdf, year_df.groupby('day')[depth].mean(), right_index=True, left_index=True)
                else:
                    newdf = pd.DataFrame(year_df.groupby('day')[depth].mean())
        idx = pd.date_range(newdf.index[0], newdf.index[-1])
        newdf = newdf.reindex(idx, fill_value=np.nan)

        # BLOCK ENDS HERE!!!!!!!

        # Creates the subplots and deletes the old plot
        if self.__plot1.axes:
            plt.Axes.remove(self.__plot1)
            plt.Axes.remove(self.__plot2)

        self.__plot = self.fig.add_subplot(111)

        color_dict = {'5': '#d4261d', '10': '#f58e6e', '15': '#fca95a', '20': '#fde5a3', '25': '#e4f4f8',
                      '30': '#a7d6e7',
                      '35': '#9ec6de', '40': '#3a6daf', '45': '#214f8a', '50': '#0a3164'}
        # Checks if there is empty depths to delete them and make them not show on the legend
        for depth in newdf.columns:
            if newdf[depth].isnull().all():
                del newdf[depth]
        newdf.plot(ax=self.__plot, zorder=10, color=[color_dict.get(x, '#333333') for x in newdf.columns])

        leg = self.__plot.legend(title='Depth (m)')

        if str(minyear) != year:
            oldepth = 0
            for depth in orderedhist_df.columns:
                if oldepth != 0:
                    self.__plot.fill_between(np.unique(orderedhist_df.index), orderedhist_df[oldepth],
                                           orderedhist_df[depth], facecolor='lightgrey', zorder=0)
                oldepth = depth
                orderedhist_df.plot(kind='line', ax=self.__plot, color='#e9e8e8', label='_nolegend_', legend=False,
                                    zorder=5)

        self.__plot.set(ylabel='Temperature (ºC) smoothed',
                      title=historical.split('_')[4] + ' year ' + year)
        self.__plot.set_yticks(np.arange(10, hismaxtemp, 2))  # Sets the limits for the Y axis
        self.__plot.set_xlim([year + '-01-01' + ' 00:00:00', str(int(year) + 1) + '-01-01' + ' 00:00:00'])

        self.savefilename = historical.split('_')[3] + '_2_' + year + '_' + historical.split('_')[4]

        # Sets the X axis as the initials of the months
        locator = mdates.MonthLocator()
        self.__plot.xaxis.set_major_locator(locator)
        fmt = mdates.DateFormatter('%b')
        self.__plot.xaxis.set_major_formatter(fmt)

        self.__plot.xaxis.set_label_text('foo').set_visible(False)
        # fig.set_size_inches(14.5, 10.5, forward=True)

        self.__plot.text(0.1, 0.1, "multi-year mean", backgroundcolor='grey')
        self.canvas.draw()

    def plot_thresholds(self, historical, toolbar, consolescreen, special=False):
        """
        Creates the thresholds plot of a given dataset

        ...

        Parameters
        ----------
        historical : str
            Path of the dataset to be loaded
        toolbar : tkinter NavigationToolbar2Tk
            Object able to create a series of buttons over the threshold plot to change
            between temperatures
        consolescreen : tkinter Text
            Object that contains the contents of the console screen
        """
        self.clear_plots()
        self.counter.append("Thresholds")
        df = self.dm.thresholds_df(historical)
        df['year'] = df['year'].astype(str)
        df['depth(m)'] = df['depth(m)'].astype(str)

        # Converts Number of operation days [N] = 0 to np.nan
        df['N'].replace(0, np.nan, inplace=True)

        dfhist_control = pd.read_csv(historical, sep='\t', dayfirst=True)
        dfhist_control['Date'] = pd.to_datetime(dfhist_control['Date'], dayfirst=True)
        dfhist_control['year'] = pd.DatetimeIndex(dfhist_control['Date'], dayfirst=True).year
        dfhist_control['month'] = pd.DatetimeIndex(dfhist_control['Date'], dayfirst=True).month
        dfhist_summer = dfhist_control.loc[
            (dfhist_control['month'] == 7) | (dfhist_control['month'] == 8) | (
                        dfhist_control['month'] == 9)]

        # Check if any depth is all nan which means there are no data for said depth
        depths = df['depth(m)'].unique()

        # We get all the years on the dataset
        years = df['year'].unique()
        years = years[years != 0]

        # Special case for Sandra's Paper - Delete after use
        if special == True:
            depths = ['10', '15', '20', '25']
            years = years[[13, 14, 15, 20]]
            df = df[(df['depth(m)'] != '5') & (df['depth(m)'] != '30') & (df['depth(m)'] != '35') & (df['depth(m)'] != '40')]
        for depth in depths:
            depth = str(depth)
            for year in df['year'].unique():
                if (dfhist_summer.loc[dfhist_summer['year'] == int(year)][depth].isnull().all()) | (dfhist_summer.loc[dfhist_summer['year'] == int(year)][depth].count() / 24 < 30):
                    for i in range(23, 29):
                        df.loc[(df['year'] == str(year)) & (df['depth(m)'] == depth), 'Ndays>=' + str(i)] = np.nan
                else:
                    print('not all na')

        # Creates the subplots and deletes the old plot
        if self.__plot1.axes:
            plt.Axes.remove(self.__plot1)
            plt.Axes.remove(self.__plot2)
        self.__plot = self.fig.add_subplot(111)

        # TODO matplotlib no tiene los mismos markers que matlab, se comprometen los 3 ultimos

        # TODO esto se puede cambiar por un Cycler y entonces no dependeria del trozo de codigo extraño de más abajo
        # Setting the properties of the line as lists to be used on a for loop depending on the year
        markers = ['+', 'o', 'x', 's', 'd', '^', 'v', 'p', 'h', '*']
        colors = ['b', 'b', 'k', 'k']
        lines = ['solid', 'dotted', 'solid', 'dotted']

        # Loop to decide each year which style has
        # TODO check code in 2030 to change this method


        # Iterates through all the years and temperatures to create a dictionary storing the needed data to plot
        maxdepth = 0  # Used to set the lowest depth as the lowest point in the Y axis
        maxdays = 0  # Used to set the maximum number of days to point in the X axis
        temperatures = {23: [], 24: [], 25: [], 26: [], 28: []}
        year_dict = {}
        # Check df to see if a given depth has less records than the next
        # Establish a max difference of records of 10 days (240 records)
        # Whole records is 2208
        # Overriding the above criteria, now established that the records cannot be different than 240 from the max one
        legend_years = years.copy()
        for year in years:
            maxndays = np.nanmax(df.loc[df['year'] == year]['N'])
            check = False
            for ni in df.loc[df['year'] == year].index:
                if maxndays - df['N'][ni] > 240:
                    df['N'][ni] = np.nan
                    for j in range(23, 29):
                        df['Ndays>=' + str(j)][ni] = np.nan
                # Check if a year has an incomplete season (under 2208 records, 92 days)
                if df['N'][ni] < 2208:
                    check = True
                else:
                    check = False
            if check == True:
                # Adds asterisk to year
                legend_years[np.where(legend_years == year)[0][0]] = year + '*'
                check = False
            for i in range(23, 29):
                yearly_plot = np.column_stack(
                    (df.loc[df['year'] == year, 'Ndays>=' + str(i)], df.loc[df['year'] == year, 'depth(m)']))
                #if yearly_plot != np.nan:
                yearly_plot[pd.isnull(yearly_plot)] = -999
                yearly_plot = yearly_plot.astype(int)
                if yearly_plot[-1, -1] > maxdepth:
                    maxdepth = yearly_plot[-1, -1]
                if np.max(yearly_plot[:, 0]) > maxdays:
                    maxdays = np.max(yearly_plot[:, 0])
                temperatures[i] = np.ma.masked_where(yearly_plot == -999, yearly_plot)
            year_dict[year] = temperatures.copy()
            self.__plot.set(ylim=(0, maxdepth + 2))
            if maxdays >= 30:
                ticks = 10
            elif maxdays >=20:
                ticks = 5
            else:
                ticks = 2
            self.__plot.set(xlim=(-2, maxdays + 2), xticks=np.arange(0, maxdays + 2, ticks))
            # Remove asterisks (if any) on years
            seq_type = type(year)
            int_year = int(seq_type().join(filter(seq_type.isdigit, year)))
            if int_year < 2000:
                color = colors[0]
                if year == years[-1]:
                    color = 'tab:orange'
                self.__plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 1990]
                               , color=color, linestyle=lines[0])
            elif int_year >= 2000 and int_year < 2010:
                color = colors[1]
                if year == years[-1]:
                    color = 'tab:orange'
                self.__plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2000],
                               color=color, linestyle=lines[1])
            elif int_year >= 2010 and int_year < 2020:
                color = colors[2]
                if year == years[-1]:
                    color = 'tab:orange'
                self.__plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2010],
                               color=color, linestyle=lines[2])
            elif int_year >= 2020 and int_year < 2030:
                color = colors[3]
                if year == years[-1]:
                    color = 'tab:orange'
                self.__plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2020],
                               color=color, linestyle=lines[3])

            self.__plot.invert_yaxis()
            self.__plot.xaxis.tick_top()
            self.canvas.draw()
        # Shrink the axis a bit to fit the legend outside of it
        box = self.__plot.get_position()
        self.__plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # Draws the legend for the different years
        legend = self.__plot.legend(legend_years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
        self.__plot.set(ylabel='Depth (m)',
                      title=historical.split('_')[4] + ' Summer (JAS) days ≥ 23ºC')
        self.__plot.xaxis.grid(True, linestyle='dashed')

        p = self.__plot.get_window_extent()
        self.__plot.annotate('*Recorded period not complete', xy=(0.68, 0.03), xycoords=p, xytext=(0.1, 0), textcoords="offset points",
                  va="center", ha="left",
                  bbox=dict(boxstyle="round", fc="w"))

        self.canvas.draw()
        # Adds tabs for the temperatures being buttons to call raiseTab and plot the Thresholds
        for i in range(23, 29):
            tab = {}
            btn = tk.Button(toolbar, text=i,
                            command=lambda i=i, maxdepth=maxdepth, maxdays=maxdays: self.__raiseTab(i, maxdepth,
                                                                                                  year_dict, markers,
                                                                                                  colors, lines, years,
                                                                                                  maxdays, historical, legend_years))
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
            tab['id'] = i
            tab['btn'] = btn
            self.__tabs[i] = tab
        self.__curtab = 23
        print('Ayo')
        self.savefilename = historical.split('_')[3] + '_3_23_' + year + '_' + historical.split('_')[4]

    def __raiseTab(self, i, maxdepth, year_dict, markers, colors, lines, years, maxdays, historical, legend_years):
        # Change between the threshold plots for different thresholds temperatures
        print(i)
        print("curtab" + str(self.__curtab))
        if self.__curtab != None and self.__curtab != i and len(self.__tabs) > 1:
            # Plot the Thresholds here and clean the last one
            self.clear_plots(clear_thresholds=False)
            self.counter.append('Thresholds')
            self.__plot = self.fig.add_subplot(111)
            if maxdays >= 30:
                ticks = 10
            elif maxdays >= 20:
                ticks = 5
            else:
                ticks = 2
            self.__plot.set(ylim=(0, maxdepth + 2))
            self.__plot.set(xlim=(-2, maxdays + 2), xticks=np.arange(0, maxdays + 2, ticks))
            for year in years:
                # Remove asterisks (if any) on years
                seq_type = type(year)
                int_year = int(seq_type().join(filter(seq_type.isdigit, year)))
                if int_year < 2000:
                    color = colors[0]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.__plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 1990]
                                   , color=color, linestyle=lines[0])
                elif int_year >= 2000 and int_year < 2010:
                    color = colors[1]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.__plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2000],
                                   color=color, linestyle=lines[1])
                elif int_year >= 2010 and int_year < 2020:
                    color = colors[2]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.__plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2010],
                                   color=color, linestyle=lines[2])
                elif int_year >= 2020 and int_year < 2030:
                    color = colors[3]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.__plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2020],
                                   color=color, linestyle=lines[3])

            self.__plot.invert_yaxis()
            self.__plot.xaxis.tick_top()
            # Shrink the axis a bit to fit the legend outside of it
            box = self.__plot.get_position()
            self.__plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            legend = self.__plot.legend(legend_years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
            self.__plot.set(ylabel='Depth (m)',
                          title=historical.split('_')[4] + ' Summer(JAS) days ≥ ' + str(i) + 'ºC')
            self.savefilename = historical.split('_')[3] + '_3_' + str(i) + '_' + year + '_' + historical.split('_')[4]

            p = self.__plot.get_window_extent()
            self.__plot.annotate('*Recorded period not complete', xy=(0.61, 0.03), xycoords=p, xytext=(0.1, 0),
                               textcoords="offset points",
                               va="center", ha="left",
                               bbox=dict(boxstyle="round", fc="w"))
            self.__plot.xaxis.grid(True, linestyle='dashed')
            self.canvas.draw()

        self.__curtab = i
        self.console_writer("Plotting for over " + str(i) + " degrees", "action")

    def clear_plots(self, clear_thresholds=True):
        """
        Deletes all current plots and plot related attributes

        ...

        Parameters
        ----------
        clear_thresholds : bool
            Bool that controls if the thresholds have been plotted to know that
            the toolbar created with them must be erased
        """
        self.console_writer('Clearing Plots', 'action')
        self.index = []
        self.counter = []
        if self.__plot.axes:
            self.__plot.clear()
            plt.Axes.remove(self.__plot)
        if self.__plot1.axes:
            self.__plot1.clear()
            self.__plot2.clear()
            plt.Axes.remove(self.__plot1)
            plt.Axes.remove(self.__plot2)
        if self.__cbexists:
            self.__cb.remove()
            self.__cbexists = False
        if clear_thresholds:
            for tab in self.__tabs:
                self.__tabs[tab]['btn'].destroy()
            self.__tabs = {}
            self.__curtab = None
        self.canvas.draw()