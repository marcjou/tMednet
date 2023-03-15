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
    global cb

    def __init__(self, f2, console, reportlogger):
        self.__set_args(f2)
        self.counter = []
        self.index = []
        self.console_writer = console
        self.reportlogger = reportlogger

    def __str__(self):
        return "GUIPlot object"

    def __set_args(self, f2):
        # Contingut de F2
        # Definir aspectes dibuix
        self.curtab = None
        self.tabs = {}
        plt.rc('legend', fontsize='medium')
        self.fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)
        self.plot = self.fig.add_subplot(111)
        self.plot1 = self.fig.add_subplot(211)
        self.plot2 = self.fig.add_subplot(212)
        plt.Axes.remove(self.plot1)
        plt.Axes.remove(self.plot2)
        plt.Axes.remove(self.plot)

        self.cbexists = False  # Control for the colorbar of the Hovmoller

        self.canvas = FigureCanvasTkAgg(self.fig, master=f2)
        self.canvas.draw()
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_args(self):
        return self.fig, self.plot, self.plot1, self.plot2, self.cbexists, self.canvas

    def plot_ts(self, mdata, files, index):
        # If there are subplots, deletes them before creating the plot anew
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)
        # if self.cbexists:
        #   self.clear_plots()

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

        # if self.plotcb.axes:
        #  plt.Axes.remove(self.plotcb)

        masked_ending_temperatures = np.ma.masked_where(np.array(mdata[index]['temp']) == 999,
                                                        np.array(mdata[index]['temp']))
        if self.plot.axes:
            # self.plot = self.fig.add_subplot(111)
            self.plot.plot(mdata[index]['time'], masked_ending_temperatures,
                           '-', label=str(mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title='Multiple depths Site: ' + str(mdata[index]['region_name']))
        else:
            self.plot = self.fig.add_subplot(111)
            self.plot.plot(mdata[index]['time'], masked_ending_temperatures,
                           '-', label=str(mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title=files[index] + "\n" + 'Depth:' + str(
                              mdata[index]['depth']) + " - Site: " + str(
                              mdata[index]['region_name']))

        self.plot.legend(title='Depth (m)')
        # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_zoom(self, mdata, files, list, cut_data_manually, controller=False):
        """
            Method: plot_zoom(self)
            Purpose: Plot a zoom of the begining and ending of the data
            Require:
                canvas: reference to canvas widget
                subplot: plot object
            Version: 05/2021, MJB: Documentation
        """
        self.clear_plots()
        index = int(list.curselection()[0])
        time_series, temperatures, indexes, start_index, valid_start, valid_end = fm.zoom_data(mdata[index], self.console_writer)

        self.counter.append(index)
        self.counter.append('Zoom')

        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        masked_temperatures = np.ma.masked_where(np.array(mdata[index]['temp']) == 999,
                                                 np.array(mdata[index]['temp']))

        self.plot1.plot(time_series[0][int(start_index):], masked_temperatures[int(start_index) + int(valid_start):len(time_series[0]) + valid_start],
                        '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
        self.plot1.legend()
        self.plot1.plot(time_series[0][:int(start_index) + 1], masked_temperatures[valid_start:int(start_index) + 1 + int(valid_start)],
                        '-', color='red', marker='o', label=str(mdata[index]['depth']))

        self.plot1.set(ylabel='Temperature (DEG C)',
                       title=files[index] + "\n" + 'Depth:' + str(
                           mdata[index]['depth']) + " - Region: " + str(
                           mdata[index]['region']))
        if indexes.size != 0:
            if indexes[0] + 1 == len(time_series[0]):
                self.plot2.plot(time_series[1][:int(indexes[0])],
                                masked_temperatures[-len(time_series[1]):(int(indexes[0]) - len(time_series[1]))],
                                '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            else:
                self.plot2.plot(time_series[1][:int(indexes[0] + 1)],
                                masked_temperatures[-len(time_series[1]):(int(indexes[0]) - len(time_series[1]) + 1)],
                                '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            self.plot2.legend()
            # Plots in the same graph the last part which represents the errors in the data from removing the sensors
            self.plot2.plot(time_series[1][int(indexes[0]):],
                            masked_temperatures[(int(indexes[0]) - len(time_series[1])):],
                            '-', color='red', marker='o', label=str(mdata[index]['depth']))
            self.plot2.set(ylabel='Temperature (DEG C)',
                           title=files[index] + "\n" + 'Depth:' + str(
                               mdata[index]['depth']) + " - Region: " + str(
                               mdata[index]['region']))
        else:
            self.plot2.plot(time_series[1],
                            masked_temperatures[-len(time_series[1]):],
                            '-', color='steelblue', marker='o', label=str(mdata[index]['depth']))
            self.plot2.legend()
            self.plot2.set(ylabel='Temperature (DEG C)',
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
            Method: plot_all_zoom(self)
            Purpose: Plot a zoom of the begining and ending of all the data loaded in the list
            Require:
                canvas: reference to canvas widget
                subplot: plot object
            Version: 05/2021, MJB: Documentation
        """
        self.clear_plots()
        index = list.curselection()

        for item in index:
            self.counter.append(item)
        self.counter.append('Zoom')

        depths = ""
        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        for i in index:
            time_series, temperatures, _, bad, bad2, bad3 = fm.zoom_data(mdata[i], self.console_writer)
            depths = depths + " " + str(mdata[i]['depth'])

            masked_temperatures = np.ma.masked_where(np.array(mdata[i]['temp']) == 999,
                                                     np.array(mdata[i]['temp']))

            masked_ending_temperatures = np.ma.masked_where(np.array(temperatures[1]) == 999,
                                                            np.array(temperatures[1]))
            self.plot1.plot(time_series[0], masked_temperatures[:len(time_series[0])],
                            '-', label=str(mdata[i]['depth']))
            self.plot1.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               mdata[i]['region']))
            self.plot1.legend()

            self.plot2.plot(time_series[1], masked_temperatures[-len(time_series[1]):],
                            '-', label=str(mdata[i]['depth']))
            self.plot2.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               mdata[i]['region']))
            self.plot2.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
        self.console_writer('Plotting zoom of depths: ', 'action', depths)
        self.console_writer(' at site ', 'action', mdata[0]['region'], True)

    def plot_dif(self, mdata):
        """
        Method: plot_dif(self)
        Purpose: Plot time series of differences
        Require:
            canvas: refrence to canvas widget
            subplot: axis object
        Version: 05/2021, MJB: Documentation
        """

        self.clear_plots()
        depths = ""
        try:
            dfdelta, _ = fm.temp_difference(mdata)
            self.counter.append('Difference')
            # Creates the subplots and deletes the old plot
            if self.plot1.axes:
                plt.Axes.remove(self.plot1)
                plt.Axes.remove(self.plot2)

            self.plot = self.fig.add_subplot(111)
            dfdelta.plot(ax=self.plot)
            self.plot.set(ylabel='Temperature (DEG C)',
                          title='Temperature differences')

            self.plot.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
            self.console_writer('Plotting zoom of depths: ', 'action', depths)
            self.console_writer(' at site ', 'action', mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_dif_filter1d(self, mdata):
        """
        Method: plot_dif_filter1d(self)
        Purpose: Plot time series of differences filtered with a 10 day running
        Require:
        Version: 05/2021, MJB: Documentation
        """

        self.clear_plots()
        depths = ""
        try:
            dfdelta = fm.apply_uniform_filter(mdata)
            self.counter.append("Filter")
            # Creates the subplots and deletes the old plot
            if self.plot1.axes:
                plt.Axes.remove(self.plot1)
                plt.Axes.remove(self.plot2)
            for _, rows in dfdelta.iterrows():  # Checks if there is an erroneous value and if there is, logs it.
                for row in rows:
                    if float(row) <= -0.2:
                        self.console_writer('Attention, value under -0.2 threshold', 'warning')
                        self.reportlogger.append('Attention, value under -0.2 threshold')
                        break
                else:
                    continue
                break

            self.plot = self.fig.add_subplot(111)
            dfdelta.plot(ax=self.plot)
            self.plot.set(ylabel='Temperature (DEG C)',
                          title='Temperature differences filtered')

            self.plot.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
            self.console_writer('Plotting zoom of depths: ', 'action', depths)
            self.console_writer(' at site ', 'action', mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_hovmoller(self, mdata):
        """
        Method: plot_hovmoller(self)
        Purpose: Plot a Hovmoller Diagram of the loaded files
        Require:
        Version: 05/2021, MJB: Documentation
        """
        try:
            self.clear_plots()
            self.counter.append("Hovmoller")
            df, depths, _ = fm.list_to_df(mdata)
            depths = np.array(depths)
            if self.plot1.axes:
                plt.Axes.remove(self.plot1)
                plt.Axes.remove(self.plot2)
            self.plot = self.fig.add_subplot(111)

            levels = np.arange(np.floor(np.nanmin(df.values)), np.ceil(np.nanmax(df.values)), 1)
            # df.resample(##) if we want to filter the results in a direct way
            # Draws a contourn line. Right now looks messy
            # ct = self.plot.contour(df.index.to_pydatetime(), -depths, df.values.T, colors='black', linewidths=0.5)
            cf = self.plot.contourf(df.index.to_pydatetime(), -depths, df.values.T, 256, extend='both', cmap='RdYlBu_r')

            cb = plt.colorbar(cf, ax=self.plot, label='Temperature (ºC)', ticks=levels)
            self.cbexists = True
            self.plot.set(ylabel='Depth (m)',
                          title='Stratification Site: ' + mdata[0]['region_name'])

            # Sets the X axis as the initials of the months
            locator = mdates.MonthLocator()
            self.plot.xaxis.set_major_locator(locator)
            fmt = mdates.DateFormatter('%b')
            self.plot.xaxis.set_major_formatter(fmt)
            # Sets the x axis on the top
            self.plot.xaxis.tick_top()

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', mdata[0]['region'], True)
        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError:
            self.console_writer('Load more than a file for the Hovmoller Diagram', 'warning')

    def clear_plots(self, clear_thresholds=True):
        """
        Method: clear_plots(self)
        Purpose: Clear plot
        Require:
            canvas: reference to canvas widget
            subplot: plot object
        Version:
        01/2021, EGL: Documentation
        """
        self.console_writer('Clearing Plots', 'action')
        self.index = []
        self.counter = []
        if self.plot.axes:
            self.plot.clear()
            plt.Axes.remove(self.plot)
        if self.plot1.axes:
            self.plot1.clear()
            self.plot2.clear()
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)
        if self.cbexists:
            cb.remove()
            self.cbexists = False
        # if self.plotcb.axes():
        #  self.plotcb.clear()
        #  plt.Axes.remove(self.plotcb)
        if clear_thresholds:
            for tab in self.tabs:
                self.tabs[tab]['btn'].destroy()
            self.tabs = {}
            self.curtab = None
        self.canvas.draw()