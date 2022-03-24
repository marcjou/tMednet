import sys
from datetime import datetime
import time
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from tkinter import messagebox, Button
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename

import pandas as pd
import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PIL import Image, ImageTk

import file_manipulation as fm
import file_writer as fw

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as dates

from datetime import timedelta

version = "0.8"
build = "Mars 2022"


class tmednet(tk.Frame):

    def __init__(self, master=None):
        """
        Method: __init__()
        Purpose: Main class constructor
        Require:
        Version:
        01/2021, EGL: Documentation
        """

        tk.Frame.__init__(self, master)  # This defines self.master

        self.master = master
        self.master.geometry("2000x1000")
        self.master.option_add('*tearOff', 'FALSE')  # menus no detaching
        self.master.resizable(True, True)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Font més gran
        def_font = tkFont.nametofont("TkDefaultFont")
        def_font.configure(size=12)
        self.master.option_add("*Font", def_font)

        # DEFINIR VARIABLES
        self.init_variables()

        # We build the GUI
        self.init_window()

    def init_window(self):
        """
        Method: init_window(self)
        Purpose: Build the GUI
        Require:
            master: master widget
        Version: 01/2021, EGL: Documentation
        """

        menubar = tk.Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.on_open)
        filemenu.add_command(label="Save", command=self.on_save)
        filemenu.add_command(label="Report", command=self.report)
        filemenu.add_separator()
        filemenu.add_command(label="Reset", command=self.reset)
        filemenu.add_command(label="Exit", command=lambda: close(self))
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="To UTC", command=self.to_utc)
        editmenu.add_command(label="Get original data", command=self.go_back)
        editmenu.add_command(label="Merge Files", command=self.merge)
        editmenu.add_command(label="Cut Endings", command=self.cut_endings)
        menubar.add_cascade(label="Edit", menu=editmenu)

        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Historical Merge', command=self.bigmerger)
        toolsmenu.add_command(label='Create Excel', command=self.create_excel)
        menubar.add_cascade(label='Tools', menu=toolsmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.master.config(menu=menubar)

        # Tabs to manipulate Thresholds Plots (refer to addTab() and raiseTab())
        self.curtab = None
        self.tabs = {}

        # General container
        fr = tk.Frame(self.master, width=1000, height=100)
        fr.grid(row=0, column=0, sticky='nsew')
        fr.grid_columnconfigure(0, weight=1)
        fr.grid_rowconfigure(0, weight=1)

        p = tk.PanedWindow(fr, sashwidth=10, sashrelief=tk.RAISED)
        p.grid(row=0, column=0, sticky="nswe")

        # F1 - F2
        f1 = tk.LabelFrame(p, text='Data', width=600)
        # f1 = tk.Frame(p)	#f1.config(bg = 'green')
        f1.grid_rowconfigure(0, weight=1)
        f1.grid_rowconfigure(1, weight=1)
        f1.grid_columnconfigure(0, weight=1)

        f2 = tk.Frame(p, width=1200, height=300)
        p.add(f1, minsize=100, width=330, padx=5)
        p.add(f2, minsize=100, padx=-5)

        # Contingut de F2
        # Definir aspectes dibuix
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
        self.toolbar = NavigationToolbar2Tk(self.canvas, f2)
        self.toolbar.children['!button5'].pack_forget()
        tk.Button(self.toolbar, text="Clear Plot", command=self.clear_plots).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)

        self.toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=0)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar.update()

        # Contingut de F1
        # Añadimos tabs

        notebook = ttk.Notebook(f1)
        frame1 = ttk.Frame(notebook)
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)
        frame2 = ttk.Frame(notebook)
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)
        notebook.add(frame1, text="Files")
        notebook.add(frame2, text="Report")
        notebook.grid(row=0, column=0, sticky="ewns")

        self.list = tk.Listbox(frame1, selectmode='extended')
        self.list.grid(row=0, column=0, sticky="ewns")
        self.list.bind("<<ListboxSelect>>", self.select_list)

        self.right_menu = Menu(frame1, tearoff=0)
        self.right_menu.add_command(label="Zoom", command=self.plot_zoom)
        self.right_menu.add_command(label="Zoom all files", command=self.plot_all_zoom)  # Placeholders
        self.right_menu.add_command(label="Plot difference", command=self.plot_dif)
        self.right_menu.add_command(label="Plot filter", command=self.plot_dif_filter1d)
        self.right_menu.add_separator()
        self.right_menu.add_command(label="Plot Hovmoller", command=self.plot_hovmoller)
        self.right_menu.add_command(label="Plot Annual T Cycles", command=self.annualcycle_browser)
        self.right_menu.add_command(label="Plot Thresholds", command=self.thresholds_browser)

        self.list.bind("<Button-3>", self.do_popup)
        cscrollb = tk.Scrollbar(frame2, width=20)
        cscrollb.grid(row=0, column=1, sticky="ns")
        self.textBox = tk.Text(frame2, bg="black", fg="white", height=10, yscrollcommand=cscrollb.set)
        self.textBox.grid(row=0, column=0, sticky="nswe")
        cscrollb.config(command=self.textBox.yview)

        self.consolescreen = tk.Text(f1, bg='black', height=1, fg='white', font='Courier 12', wrap='word')
        self.consolescreen.grid(row=1, column=0, sticky='nsew')
        self.consolescreen.bind("<Key>", lambda e: "break")  # Makes the console uneditable
        self.consolescreen.tag_config('warning', foreground="firebrick3")
        self.consolescreen.tag_config('action', foreground="steelblue4", font='Courier 12 bold')

    # p.add(f1,width=300)
    # p.add(f2,width=1200)
    def init_variables(self):
        """
        Method: init_variables(self)
        Purpose: Initializes the variables
        Require:
        Version: 11/2021, MJB: Documentation
        """
        # DEFINIR VARIABLES
        self.path = ""
        self.files = []
        self.mdata = []
        self.index = []
        self.newfiles = 0
        self.counter = []
        self.recoverindex = None
        self.recoverindexpos = None
        self.reportlogger = []
        self.tempdataold = []
        self.controlevent = False

    def console_writer(self, msg, mod, var=False, liner=False):
        """
                Method: console_writer(self, msg, mod, var=False, liner=False)
                Purpose: Writes messages to the console
                Require:
                    msg: The message that the console will output
                    mod: Modifier for the message (if it is a warning, an action...)
                    var: If there is an additional variable to be added to the message. False by default.
                    liner: Controls when to end the message with '==='. False by default.
                Version: 05/2021, MJB: Documentation
                """
        if var:
            self.consolescreen.insert("end", msg, mod)
            self.consolescreen.insert("end", str(var))
            if liner:
                self.consolescreen.insert("end", "\n =============\n")
            self.consolescreen.see('end')
        else:
            self.consolescreen.insert("end", msg + "\n", mod)
            self.consolescreen.insert("end", "=============\n")
            self.consolescreen.see('end')

    def do_popup(self, event):
        """
        Method: do_popup(self, event)
        Purpose: Event controller to raise a right-click menu
        Require:
        Version: 05/2021, MJB: Documentation
        """
        try:
            self.right_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_menu.grab_release()

    def select_list(self, evt):
        """
        Method: select_list(self, evt)
        Purpose: Event handler for when an item of the list is selected
        Require:
        Version: 05/2021, MJB: Documentation
        """
        try:

            w = evt.widget
            index = int(w.curselection()[0])
            if index in self.index:
                pass
            else:
                self.value = w.get(index)
                print(index, self.value)
                self.console_writer('Plotting: ', 'action', self.value, True)
                self.index.append(index)
                #Checks if the last plot was a Zoom to delete the data
                if self.counter:
                    if self.counter[-1] == 'Zoom':
                        self.clear_plots()
                self.counter.append(index)  # Keeps track of how many plots there are and the index of the plotted files
                # dibuixem un cop seleccionat
                self.plot_ts(index)
        except IndexError:
            pass  # Not knowing why this error raises when Saving the file but doesn't affect the code. Should check.

        # fm.load_data(self)  Que fa això aquí???? Investigar [[DEPRECATED??]]

    def on_open(self):
        """
        Method: on_open(self)
        Purpose: Launches the askopen widget to set data filenames
        Require:
        Version: 01/2021, EGL: Documentation
        """

        self.path = "./"
        files = askopenfilenames(initialdir='../src', title="Open files",
                                 filetypes=[("All files", "*.*")])
        try:
            filesname, self.path = fm.openfile(self, files, self.consolescreen)
            for file in filesname:  # Itera toda la lista de archivos para añadirlos a la listbox
                self.files.append(file)
            fm.load_data(self, self.consolescreen)  # Llegim els fitxers
        except TypeError:
            self.console_writer('Unable to read file', 'warning')
        return

    def report(self):
        """
        Method: report(self)
        Purpose: List main file characteristics
        Require:
            textBox: text object
        Version: 01/2021, EGL: Documentation
        """

        fm.report(self, self.textBox)

    def reset(self):
        """
        Method: reset(self)
        Purpose: Reset the parameters and clear the lists, plots, console and report windows
        Require:
        Version: 11/2021, MJB: Documentation
        """
        self.clear_plots()
        self.list.delete(0, END)
        self.textBox.delete('1.0', END)
        self.consolescreen.delete('1.0', END)
        self.init_variables()

    def to_utc(self):
        """
        Method: to_utc(self)
        Purpose: Shift temporal axis
        Require:
        Version: 01/2021, EGL: Documentation
        """
        if not self.mdata:
            self.console_writer('Please, load a file before converting to UTC', 'warning')
        else:
            try:
                fm.to_utc(self.mdata)
            except IndexError:
                self.console_writer('Please, load a file before converting to UTC', 'warning')

    def plot_ts(self, index):
        """
        Method: plot_ts(self)
        Purpose: Plot a time series
        Require:
            canvas: reference to canvas widget
            subplot: plot object
        Version:
        01/2021, EGL: Documentation
        """
        # If there are subplots, deletes them before creating the plot anew
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)
        #if self.cbexists:
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

        masked_ending_temperatures = np.ma.masked_where(np.array(self.mdata[index]['temp']) == 999,
                                                        np.array(self.mdata[index]['temp']))
        if self.plot.axes:
            # self.plot = self.fig.add_subplot(111)
            self.plot.plot(self.mdata[index]['time'], masked_ending_temperatures,
                           '-', label=str(self.mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title='Multiple depths Site: ' + str(self.mdata[index]['region_name']))
        else:
            self.plot = self.fig.add_subplot(111)
            self.plot.plot(self.mdata[index]['time'], masked_ending_temperatures,
                           '-', label=str(self.mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title=self.files[index] + "\n" + 'Depth:' + str(
                              self.mdata[index]['depth']) + " - Site: " + str(
                              self.mdata[index]['region_name']))

        self.plot.legend(title='Depth (m)')
        # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_zoom(self, controller=False):
        """
            Method: plot_zoom(self)
            Purpose: Plot a zoom of the begining and ending of the data
            Require:
                canvas: reference to canvas widget
                subplot: plot object
            Version: 05/2021, MJB: Documentation
        """
        self.clear_plots()
        index = int(self.list.curselection()[0])
        time_series, temperatures, indexes, start_index = fm.zoom_data(self.mdata[index], self.consolescreen)

        self.counter.append(index)
        self.counter.append('Zoom')

        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        masked_temperatures = np.ma.masked_where(np.array(self.mdata[index]['temp']) == 999,
                                                 np.array(self.mdata[index]['temp']))

        self.plot1.plot(time_series[0][int(start_index):], masked_temperatures[int(start_index):len(time_series[0])],
                        '-', color='steelblue', marker='o', label=str(self.mdata[index]['depth']))
        self.plot1.legend()
        self.plot1.plot(time_series[0][:int(start_index) + 1], masked_temperatures[:int(start_index) + 1],
                        '-', color='red', marker='o', label=str(self.mdata[index]['depth']))

        self.plot1.set(ylabel='Temperature (DEG C)',
                       title=self.files[index] + "\n" + 'Depth:' + str(
                           self.mdata[index]['depth']) + " - Region: " + str(
                           self.mdata[index]['region']))
        if indexes.size != 0:
            self.plot2.plot(time_series[1][:int(indexes[0] + 1)],
                            masked_temperatures[-len(time_series[0]):(int(indexes[0]) - len(time_series[0]) + 1)],
                            '-', color='steelblue', marker='o', label=str(self.mdata[index]['depth']))
            self.plot2.legend()
            # Plots in the same graph the last part which represents the errors in the data from removing the sensors
            self.plot2.plot(time_series[1][int(indexes[0]):],
                            masked_temperatures[(int(indexes[0]) - len(time_series[0])):],
                            '-', color='red', marker='o', label=str(self.mdata[index]['depth']))
            self.plot2.set(ylabel='Temperature (DEG C)',
                           title=self.files[index] + "\n" + 'Depth:' + str(
                               self.mdata[index]['depth']) + " - Region: " + str(
                               self.mdata[index]['region']))
        else:
            self.plot2.plot(time_series[1],
                            masked_temperatures[-len(time_series[0]):],
                            '-', color='steelblue', marker='o', label=str(self.mdata[index]['depth']))
            self.plot2.legend()
            self.plot2.set(ylabel='Temperature (DEG C)',
                           title=self.files[index] + "\n" + 'Depth:' + str(
                               self.mdata[index]['depth']) + " - Region: " + str(
                               self.mdata[index]['region']))
        # fig.set_size_inches(14.5, 10.5, forward=True)
        # Controls if we are accesing the event handler through a real click or it loops.
        if not controller:
            cid = self.fig.canvas.mpl_connect('button_press_event', lambda event: self.cut_data_manually(event, index))

        self.canvas.draw()
        self.console_writer('Plotting zoom of depth: ', 'action', self.mdata[0]['depth'])
        self.console_writer(' at site ', 'action', self.mdata[0]['region'], True)

    def cut_data_manually(self, event, ind):
        """
        Method: cut_data_manually(self, event, ind)
        Purpose: Event controller to cut the data by selecting the plot
        Require:
            ind: Index of the data to be cut
        Version: 05/2021, MJB: Documentation
        """
        # TODO Fix a bug that duplicates the event handler click when using the Go_Back function
        try:
            xtime = dates.num2date(event.xdata)
            xtime_rounded = xtime.replace(second=0, microsecond=0, minute=0, hour=xtime.hour) + timedelta(
                hours=xtime.minute // 30)
            xtime_rounded = xtime_rounded.replace(tzinfo=None)
            index = self.mdata[ind]['time'].index(xtime_rounded)
            print('Cutting data')
            self.console_writer('Cutting data at depth: ', 'action', self.mdata[ind]['depth'])
            self.console_writer(' at site ', 'action', self.mdata[ind]['region'], True)

            if self.recoverindex:
                self.recoverindex.append(ind)
            else:
                self.recoverindex = [ind]
            # self.tempdataold.append(self.mdata[ind]['temp'].copy())

            if index < 50:
                for i in range(len(self.mdata[ind]['temp'][:index])):
                    self.mdata[ind]['temp'][i] = 999
            else:
                for i in range(1, len(self.mdata[ind]['temp'][index:])):
                    self.mdata[ind]['temp'][i + index] = 999
        except ValueError:
            self.console_writer('Select value that is not the start or ending', 'warning')
            return

    def plot_all_zoom(self):
        """
            Method: plot_all_zoom(self)
            Purpose: Plot a zoom of the begining and ending of all the data loaded in the list
            Require:
                canvas: reference to canvas widget
                subplot: plot object
            Version: 05/2021, MJB: Documentation
        """
        self.clear_plots()
        index = self.list.curselection()

        for item in index:
            self.counter.append(item)
        self.counter.append('Zoom')

        depths = ""
        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        for i in index:
            time_series, temperatures, _, bad = fm.zoom_data(self.mdata[i], self.consolescreen)
            depths = depths + " " + str(self.mdata[i]['depth'])

            masked_temperatures = np.ma.masked_where(np.array(self.mdata[i]['temp']) == 999,
                                                     np.array(self.mdata[i]['temp']))

            masked_ending_temperatures = np.ma.masked_where(np.array(temperatures[1]) == 999,
                                                            np.array(temperatures[1]))
            self.plot1.plot(time_series[0], masked_temperatures[:len(time_series[0])],
                            '-', label=str(self.mdata[i]['depth']))
            self.plot1.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               self.mdata[i]['region']))
            self.plot1.legend()

            self.plot2.plot(time_series[1], masked_temperatures[-len(time_series[0]):],
                            '-', label=str(self.mdata[i]['depth']))
            self.plot2.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               self.mdata[i]['region']))
            self.plot2.legend()

            # fig.set_size_inches(14.5, 10.5, forward=True)
            self.canvas.draw()
        self.console_writer('Plotting zoom of depths: ', 'action', depths)
        self.console_writer(' at site ', 'action', self.mdata[0]['region'], True)

    def plot_dif(self):
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
            dfdelta, _ = fm.temp_difference(self.mdata)
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
            self.console_writer(' at site ', 'action', self.mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_dif_filter1d(self):
        """
        Method: plot_dif_filter1d(self)
        Purpose: Plot time series of differences filtered with a 10 day running
        Require:
        Version: 05/2021, MJB: Documentation
        """

        self.clear_plots()
        depths = ""
        try:
            dfdelta = fm.apply_uniform_filter(self.mdata)
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
            self.console_writer(' at site ', 'action', self.mdata[0]['region'], True)
        except UnboundLocalError:
            self.console_writer('Load more than a file for plotting the difference', 'warning')

    def plot_hovmoller(self):
        """
        Method: plot_hovmoller(self)
        Purpose: Plot a Hovmoller Diagram of the loaded files
        Require:
        Version: 05/2021, MJB: Documentation
        """
        try:

            fm.to_utc(self.mdata)
            global cb
            self.clear_plots()
            self.counter.append("Hovmoller")
            df, depths, _ = fm.list_to_df(self.mdata)
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
                          title='Stratification Site: ' + self.mdata[0]['region_name'])

            # Sets the X axis as the initials of the months
            locator = mdates.MonthLocator()
            self.plot.xaxis.set_major_locator(locator)
            fmt = mdates.DateFormatter('%b')
            self.plot.xaxis.set_major_formatter(fmt)
            #Sets the x axis on the top
            self.plot.xaxis.tick_top()

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', self.mdata[0]['region'], True)
        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError:
            self.console_writer('Load more than a file for the Hovmoller Diagram', 'warning')

    def plot_annualTCycle(self):
        """
        Method: annualTCycle(self)
        Purpose: Plots the Annual T Cycles plot for the loaded files
        Require:
        Version: 09/2021, MJB: Documentation
        """

        # Gets the historical data to calculate the multi-year mean and deletes the old plots
        historical = self.openfileinput.get()
        self.newwindow.destroy()
        self.clear_plots()
        self.counter.append("Cycles")

        excel_object = fw.Excel(historical, write_excel=False, seasonal=False)  # returns an excel object
        histdf = excel_object.monthlymeandf

        dfdelta = fm.running_average(self.mdata, running=360)

        # All this block serves only to transform the data from hourly to daily. It should be inside its own method
        daylist = []
        for time in dfdelta.index:
            old = datetime.strftime(time, '%Y-%m-%d')
            new = datetime.strptime(old, '%Y-%m-%d')
            daylist.append(new)
        dfdelta['day'] = daylist
        newdf = None
        for depth in dfdelta.columns:
            if depth != 'day':
                if newdf is not None:
                    newdf = pd.merge(newdf, dfdelta.groupby('day')[depth].mean(), right_index=True, left_index=True)
                else:
                    newdf = pd.DataFrame(dfdelta.groupby('day')['5'].mean())

        # BLOCK ENDS HERE!!!!!!!

        #TODO Why the filter does not look the same? ASk Nathaniel
        #TODO change the x axis to reflect the name of the month

        # Dict to change from string months to datetime

        monthDict = {}
        for i in range(1, 13):
            if i < 10:
                monthDict['0'+str(i)] = datetime.strptime(datetime.strftime(dfdelta.index[0], '%Y')+'-0' + str(i) + '-01',
                                                          '%Y-%m-%d')
            else:
                monthDict[str(i)] = datetime.strptime(
                    datetime.strftime(dfdelta.index[0], '%Y') + '-' + str(i) + '-01',
                '%Y-%m-%d')


        # Creates the subplots and deletes the old plot
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)

        self.plot = self.fig.add_subplot(111)



        for month in histdf['month'].unique():
            histdf['month'].replace(month, monthDict[month], inplace=True)
        usedf = histdf.copy()
        usedf.set_index('month', inplace=True)
        usedf.sort_index(inplace=True)
        oldepth = 0
        for depth in usedf['depth'].unique():
            if oldepth != 0:
                self.plot.fill_between(np.unique(usedf.index), usedf.loc[usedf['depth'] == oldepth]['mean'],
                                       usedf.loc[usedf['depth'] == depth]['mean'], facecolor='lightgrey')
            oldepth = depth

        for depth in histdf['depth'].unique():
            histdf.loc[histdf['depth'] == depth].plot(kind='line', x='month', y='mean', ax=self.plot, color='white',
                                                      label='_nolegend-', legend=False)


        newdf.plot(ax=self.plot)
        self.plot.set(ylabel='Temperature (ºC) smoothed',
                      title='Annual T Cycles')
        self.plot.set_ylim([10, 28]) #Sets the limits for the Y axis
        self.plot.legend(title='Depth (m)')

        #Sets the X axis as the initials of the months
        locator = mdates.MonthLocator()
        self.plot.xaxis.set_major_locator(locator)
        fmt = mdates.DateFormatter('%b')
        self.plot.xaxis.set_major_formatter(fmt)

        self.plot.xaxis.set_label_text('foo').set_visible(False)
                # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_thresholds(self):
        """
       Method: plot_thresholds(self)
       Purpose: Creates the thresholds graph
       Require:
       Version: 11/2021, MJB: Documentation
       """
        historical = self.openfileinput.get()
        #Deprecating region input as it can be gotten automatically from the filename (self.mdata[0]['region_name'])
        #region = self.regioninput.get()
        self.newwindow.destroy()
        self.clear_plots()
        self.counter.append("Thresholds")
        excel_object = fw.Excel(historical, write_excel=False, console=self.consolescreen)  # returns an excel object
        df = excel_object.mydf3

        # Creates the subplots and deletes the old plot
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)
        self.plot = self.fig.add_subplot(111)


        # TODO matplotlib no tiene los mismos markers que matlab, se comprometen los 3 ultimos

        # Setting the properties of the line as lists to be used on a for loop depending on the year
        markers = ['+', 'o', 'x', 's', 'd', '^', 'v', 'p', 'h', '*']
        colors = ['b', 'b', 'k', 'k']
        lines = ['solid', 'dotted', 'solid', 'dotted']

        # Loop to decide each year which style has
        #TODO check code in 2030 to change this method
        # We get all the years on the dataset
        years = df['year'].unique()
        # Iterates through all the years and temperatures to create a dictionary storing the needed data to plot
        maxdepth = 0  # Used to set the lowest depth as the lowest point in the Y axis
        maxdays = 0   # Used to set the maximum number of days to point in the X axis
        temperatures = {23: [], 24: [], 25: [], 26: [], 28: []}
        year_dict = {}
        for year in years:
            for i in range(23, 29):
                yearly_plot = np.column_stack(
                    (df.loc[df['year'] == year, 'Ndays>=' + str(i)], df.loc[df['year'] == year, 'depth(m)']))
                yearly_plot = yearly_plot.astype(int)
                if yearly_plot[-1, -1] > maxdepth:
                    maxdepth = yearly_plot[-1, -1]
                if np.max(yearly_plot[:, 0]) > maxdays:
                    maxdays = np.max(yearly_plot[:, 0])
                temperatures[i] = np.copy(yearly_plot)
            year_dict[year] = temperatures.copy()
            self.plot.set(ylim=(0, maxdepth + 2))
            self.plot.set(xlim=(-2, maxdays + 2))
            if int(year) < 2000:
                color = colors[0]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int(year) - 1990]
                               , color=color, linestyle=lines[0])
            elif int(year) >= 2000 and int(year) < 2010:
                color = colors[1]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int(year) - 2000],
                               color=color, linestyle=lines[1])
            elif int(year) >= 2010 and int(year) < 2020:
                color = colors[2]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int(year) - 2010],
                               color=color, linestyle=lines[2])
            elif int(year) >= 2020 and int(year) < 2030:
                color = colors[3]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int(year) - 2020],
                               color=color, linestyle=lines[3])

            self.plot.invert_yaxis()
            self.plot.xaxis.tick_top()
            self.canvas.draw()
        #Shrink the axis a bit to fit the legend outside of it
        box = self.plot.get_position()
        self.plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # Draws the legend for the different years
        self.plot.legend(years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
        self.plot.set(ylabel='Depth (m)',
                      title=self.mdata[0]['region_name'] + ' Summer days ≥ 23ºC')
        self.canvas.draw()
        # Adds tabs for the temperatures being buttons to call raiseTab and plot the Thresholds
        for i in range(23, 29):
            tab = {}
            btn = tk.Button(self.toolbar, text=i,
                            command=lambda i=i, maxdepth=maxdepth, maxdays=maxdays: self.raiseTab(i, maxdepth, year_dict, markers,
                                                                                 colors, lines, years, maxdays))
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
            tab['id'] = i
            tab['btn'] = btn
            self.tabs[i] = tab
        self.curtab = 23
        print('Ayo')

    def raiseTab(self, i, maxdepth, year_dict, markers, colors, lines, years, maxdays):
        """
           Method: raiseTab(self, i, maxdepth, year_dict, markers, colors, lines, years, region))
           Purpose: Changes the tab being plotted for the thresholds between the different temperatures needed
           Require:
                i: Temperature to be plotted
                maxdepth: The maximum depth to plot on the y-axis
                year_dict: The dictionary with the data for all the years
                markers: The dictionary of markers
                colors: The dictionary of colors
                lines: The dictionary of lines
                years: A list with all the years on the data
                region: The name of the region to be plotted to use as the title of the graph
           Version: 11/2021, MJB: Documentation
           """
        print(i)
        print("curtab" + str(self.curtab))
        if self.curtab != None and self.curtab != i and len(self.tabs) > 1:
            # Plot the Thresholds here and clean the last one
            self.clear_plots(clear_thresholds=False)
            self.counter.append('Thresholds')
            self.plot = self.fig.add_subplot(111)
            self.plot.set(ylim=(0, maxdepth))
            self.plot.set(xlim=(0, maxdays))
            for year in years:
                if int(year) < 2000:
                    color = colors[0]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int(year) - 1990]
                                   , color=color, linestyle=lines[0])
                elif int(year) >= 2000 and int(year) < 2010:
                    color = colors[1]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int(year) - 2000],
                                   color=color, linestyle=lines[1])
                elif int(year) >= 2010 and int(year) < 2020:
                    color = colors[2]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int(year) - 2010],
                                   color=color, linestyle=lines[2])
                elif int(year) >= 2020 and int(year) < 2030:
                    color = colors[3]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int(year) - 2020],
                                   color=color, linestyle=lines[3])

            self.plot.invert_yaxis()
            self.plot.xaxis.tick_top()
            # Shrink the axis a bit to fit the legend outside of it
            box = self.plot.get_position()
            self.plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            self.plot.legend(years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
            self.plot.set(ylabel='Depth (m)',
                          title=self.mdata[0]['region_name'] + ' Summer days ≥ ' + str(i) + 'ºC')
            self.canvas.draw()

        self.curtab = i
        self.console_writer("Plotting for over " + str(i) + " degrees", "action")

    def thresholds_browser(self):
        """
            Method: thresholds_browser(self)
            Purpose: Opens a new window to select the file to be opened as well as to write the name of the region
            Require:
            Version: 11/2021, MJB: Documentation
          """
        self.newwindow = Toplevel()
        self.newwindow.title('Select historical file')

        openfileLabel = Label(self.newwindow, text='Historical:').grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        openfileBrowse = Button(self.newwindow, text='Browse', command=self.browse_file).grid(row=0, column=2)
        #regionLabel = Label(self.newwindow, text='Region:').grid(row=1, pady=10)
        #self.regioninput = Entry(self.newwindow, width=20)
        #self.regioninput.grid(row=1, column=1)
        actionButton = Button(self.newwindow, text='Select', command=self.plot_thresholds).grid(row=1, column=1)

    def annualcycle_browser(self):
        """
            Method: annualcycle_browser(self)
            Purpose: Opens a new window to select the file to be opened
            Require:
            Version: 11/2021, MJB: Documentation
          """
        self.newwindow = Toplevel()
        self.newwindow.title('Select historical file')

        openfileLabel = Label(self.newwindow, text='Historical:').grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        openfileBrowse = Button(self.newwindow, text='Browse', command=self.browse_file).grid(row=0, column=2)
        actionButton = Button(self.newwindow, text='Select', command=self.plot_annualTCycle).grid(row=1, column=1)

    def go_back(self):
        """
        Method: go_back(self)
        Purpose: Returns to the original data, before applying any cuts
        Require:
        Version: 05/2021, MJB: Documentation
        """
        try:
            if self.recoverindex:
                for i in self.recoverindex:
                    self.mdata[i]['temp'] = self.tempdataold[i]['temp'].copy()
                self.recoverindex = None
                # self.tempdataold = None
            else:
                i = 0
                for data in self.mdata:
                    data['temp'] = self.tempdataold[i]['temp'].copy()
                    i += 1
            self.console_writer('Recovering old data', 'action')
            self.clear_plots()
        except (AttributeError, TypeError):
            self.console_writer('Cut the ending of a file before trying to recover it', 'warning')

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

    def cut_endings(self):
        """
        Method: cut_endings(self)
        Purpose: Cuts the endings of the data that is considered 'not real' (from the fm.zoom_data function)
        Require:
        Version: 05/2021, MJB: Documentation
        """
        if self.mdata:
            # self.tempdataold = []
            for data in self.mdata:
                # self.tempdataold.append(data['temp'].copy())
                _, temperatures, indexes, start_index = fm.zoom_data(data, self.consolescreen)
                for i in indexes:
                    data['temp'][int(i) - len(np.array(temperatures[1]))] = 999
                for i in range(0, int(start_index)):
                    data['temp'][int(i)] = 999
            self.console_writer('Endings of all the files cut', 'action', liner=True)
            self.reportlogger.append('Endings and start automatically cut')
        else:
            self.console_writer('Load a file before trying to cut it', 'warning')

    def on_save(self):
        """
        Method: on_save(self)
        Purpose: Saves the file with a proposed name and lets the user choose one of their liking.
        Require:
        Version:
        05/2021, MJB: Documentation
        """
        try:  # If there is no plot, it shows an error message

            if self.counter[-1] == 'Zoom':
                zoom = self.counter.pop()
            else:
                zoom = ''

            if len(self.counter) == 1:  # Writes the default name of the image file according to the original file
                if self.counter[0] == "Hovmoller":
                    filename = str(self.value[:-7]) + " Hovmoller"
                elif self.counter[0] == 'Cycles':
                    filename = str(self.value[:-7]) + " Annual T-Cycles"
                elif self.counter[0] == 'Thresholds':
                    filename = str(self.value[:-7]) + " Thresholds"
                elif self.counter[0] == 'Filter':
                    filename = str(self.value[:-7]) + " filtered differences"
                elif self.counter[0] == 'Difference':
                    filename = str(self.value[:-7]) + " differences"
                else:
                    filename = self.value[:-4] + ' ' + zoom
            if len(self.counter) > 1:

                filename = ""
                for n in self.counter:
                    filename = filename + "_" + self.files[n][-6:-4]
                filename = self.mdata[0]["datainici"].strftime("%Y-%m-%d") + "_" \
                           + self.mdata[0]["datafin"].strftime("%Y-%m-%d") + "_Combo of depths" + filename + ' ' + zoom

            file = asksaveasfilename(initialdir='../src/output_images',
                                     filetypes=(("PNG Image", "*.png"), ("JPG Image", "*.jpg"), ("All Files", "*.*")),
                                     defaultextension='.png', initialfile=filename, title="Save as")
            if zoom == 'Zoom':
                self.counter.append(zoom)
            if file:
                self.fig.savefig(file)
                self.mdata[0]['images'].append(file) #Stores the path of the created images to print them on the report
                self.console_writer('Saving plot in: ', 'action', file, True)
        except (AttributeError, UnboundLocalError, IndexError):
            self.console_writer('Error, couldn\'t find a plot to save', 'warning')

    def merge(self):
        """
        Method: merge(self)
        Purpose: Merges all of the loaded files into a single geojson one
        Require:
        Version:
        05/2021, MJB: Documentation
        """


        try:
            if not self.mdata[0]['time']:
                self.console_writer('First select \'To UTC\' option', 'warning')
            else:
                self.console_writer('Creating Geojson', 'action')
                df, depths, SN, merging = fm.merge(self)
                if merging is False:
                    self.console_writer('Load more than a file for merging, creating an output of only a file instead',
                                        'warning')
                start_time = time.time()
                fm.df_to_geojson(df, depths, SN, self.mdata[0]['latitude'], self.mdata[0]['longitude'])
                fm.df_to_txt(df, self.mdata[0], SN)
                self.consolescreen.insert("end", "--- %s seconds spend to create a geojson ---" % (
                        time.time() - start_time) + "\n =============\n")
                self.reportlogger.append('Geojson and CSV file created')
        except IndexError:
            self.console_writer('Please, load a file first', 'warning')

    def create_excel(self):
        """
        Method: create_excel(self)
        Purpose: Loads a new window with the options to select the file from which the new excel will be created and
                the name of the Excel file
        Require:
        Version:
        11/2021, MJB: Documentation
        """
        self.newwindow = Toplevel()
        self.newwindow.title('Create Excel')

        openfileLabel = Label(self.newwindow, text='Input:').grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        openfileBrowse = Button(self.newwindow, text='Browse', command=self.browse_file).grid(row=0, column=2)
        writefileLabel = Label(self.newwindow, text='Output file name:').grid(row=1, pady=10)
        self.writefileinput = Entry(self.newwindow, width=20)
        self.writefileinput.grid(row=1, column=1)
        writefile = Button(self.newwindow, text='Write', command=self.write_excel).grid(row=1, column=2)

    def bigmerger(self):
        """
        Method: bigmerger(self)
        Purpose: Creates a new window in order for the user to select the files and filenames for the historical
                merger function
        Require:
        Version:
        11/2021, MJB: Documentation
        """
        self.newwindow = Toplevel()
        self.newwindow.title('Create Merge Historical')

        openfileLabel = Label(self.newwindow, text='Historical:').grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        openfileBrowse = Button(self.newwindow, text='Browse', command=self.browse_file).grid(row=0, column=2)
        openfileLabel2 = Label(self.newwindow, text='New:').grid(row=1, pady=10)
        self.openfileinput2 = Entry(self.newwindow, width=20)
        self.openfileinput2.grid(row=1, column=1)
        openfileBrowse2 = Button(self.newwindow, text='Browse', command=lambda: self.browse_file(True)).grid(row=1,
                                                                                                             column=2)
        writefileLabel = Label(self.newwindow, text='Output file name:').grid(row=2, pady=10)
        self.writefileinput = Entry(self.newwindow, width=20)
        self.writefileinput.grid(row=2, column=1)
        writefile = Button(self.newwindow, text='Write',
                           command=lambda: self.call_merger(self.openfileinput.get(), self.openfileinput2.get(),
                                                            self.writefileinput.get())).grid(row=2, column=2)

    def call_merger(self, filename1, filename2, output):
        """
        Method: call_merger(self, filename1, filename2, output)
        Purpose: Calls the bigmerger function under file_writer
        Require:
            filename1: The path of the historical file
            filename2: The path of the file to merge
            output: The name of the final output
        Version:
        11/2021, MJB: Documentation
        """
        self.newwindow.destroy()
        self.console_writer('Historical Merge successful!', 'action')
        fw.big_merge(filename1, filename2, output)

    def write_excel(self):
        """
        Method: write_excel(self)
        Purpose: Informs the report and launches the write_excel function
        Require:
        Version:
        11/2021, MJB: Documentation
        """
        self.console_writer('Writing the Excel file, please wait this could take some minutes...', 'action')
        input = self.openfileinput.get()
        output = self.writefileinput.get()
        self.newwindow.destroy()
        fw.Excel(input, '../src/output_files/' + output + '.xlsx')
        self.console_writer('Excel file successfully created!', 'action')

    def browse_file(self, merge=False):
        """
        Method: browse_file(self)
        Purpose: Browses directories and stores the file selected into a variable
        Require:
        Version:
        11/2021, MJB: Documentation
        """
        if merge:
            self.openfileinput2.delete(0, END)
            file = askopenfilename(initialdir='../src/')
            self.openfileinput2.insert(0, file)
        else:
            self.openfileinput.delete(0, END)
            file = askopenfilename(initialdir='../src/')
            self.openfileinput.insert(0, file)

    @staticmethod
    def help():
        """
        Method: help()
        Purpose: Shows an 'About' message
        Require:
        Version: 05/2021, MJB: Documentation
        """

        top = Toplevel()
        top.title("About...")

        img = Image.open("../res/logos/TMEDNET_White.png").resize((250, 78))
        photo = ImageTk.PhotoImage(img)
        label = Label(top, image=photo)
        label.image = photo  # keep a reference!
        text = Label(top, text='Version: ' + version + '\nAuthor: Marc Jou \nBuild: ' + build)
        label.pack()
        text.pack()
        # messagebox.showinfo('About', 'Version: ' + version + '\nAuthor: Marc Jou \nBuild: ' + build)
        pass


def close(root):
    """
    Function: close():
    Purpose: To quit and close the GUI
    Input:
        root (obsject): reference to toplevel tkinter widget
    Requires:
        sys: module
    Version:
        01/2021, EGL: Documentation
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        sys.exit()
