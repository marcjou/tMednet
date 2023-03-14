import sys
import time
import matplotlib
import GUI_plots as gp
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

version = "0.8"
build = "Mars 2022"
matplotlib.use("TkAgg")


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
        toolsmenu.add_command(label='Create Excel',
                              command=lambda: self.window_browser('Select file and output file name',
                                                                  self.write_excel, 'Input: '))
        toolsmenu.add_command(label='Create netCDF',
                              command=lambda: self.window_browser('Select historical file',
                                                                  self.generate_netCDF, 'Historical: '))
        toolsmenu.add_command(label='Create Heat spikes',
                              command=lambda: self.window_browser('Select historical file',
                                                                  self.create_heat_spikes, 'Historical: ', 'Year'))
        toolsmenu.add_command(label='Create anomalies',
                              command=lambda: self.window_browser('Select historical file',
                                                                  self.create_anomalies, 'Historical: ', 'Year'))
        toolsmenu.add_command(label='Create tridepth anomalies',
                              command=lambda: self.window_browser('Select historical file',
                                                                  self.create_tridepth_anomalies, 'Historical: ', 'Year'))
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
        self.gui_plot = gp.GUIPlot(f2, self.console_writer)
        self.fig, self.plot, self.plot1, self.plot2, self.cbexists, self.canvas = self.gui_plot.get_args()
        self.toolbar = NavigationToolbar2Tk(self.canvas, f2)
        self.toolbar.children['!button5'].pack_forget()
        tk.Button(self.toolbar, text="Clear Plot", command=self.gui_plot.clear_plots).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)

        self.toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=0)
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
        self.right_menu.add_command(label="Zoom", command=lambda: self.gui_plot.plot_zoom(self.mdata, self.files, self.list, self.cut_data_manually))
        self.right_menu.add_command(label="Zoom all files", command=lambda: self.gui_plot.plot_all_zoom(self.mdata, self.list))  # Placeholders
        self.right_menu.add_command(label="Plot difference", command=self.plot_dif)
        self.right_menu.add_command(label="Plot filter", command=self.plot_dif_filter1d)
        self.right_menu.add_separator()
        self.right_menu.add_command(label="Plot Hovmoller", command=self.plot_hovmoller)
        self.right_menu.add_command(label="Plot Stratification",
                                    command=lambda: self.window_browser('Select historical file and year',
                                                                        self.plot_stratification, 'Historical: ',
                                                                        'Year: '))
        self.right_menu.add_command(label="Plot Annual T Cycles",
                                    command=lambda: self.window_browser('Select historical file and year',
                                                                        self.plot_annualTCycle, 'Historical: ',
                                                                        'Year: '))
        self.right_menu.add_command(label="Plot Thresholds",
                                    command=lambda: self.window_browser('Select historical file',
                                                                        self.plot_thresholds, 'Historical: '))

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
        self.savefilename = ''

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
            if index in self.gui_plot.index:
                pass
            else:
                self.value = w.get(index)
                print(index, self.value)
                self.console_writer('Plotting: ', 'action', self.value, True)
                self.gui_plot.index.append(index)
                # Checks if the last plot was a Zoom to delete the data
                if self.gui_plot.counter:
                    if self.gui_plot.counter[-1] == 'Zoom':
                        self.gui_plot.clear_plots()
                self.gui_plot.counter.append(index)  # Keeps track of how many plots there are and the index of the plotted files
                # dibuixem un cop seleccionat
                self.gui_plot.plot_ts(self.mdata, self.files, index)

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
        except TypeError as e:
            self.console_writer('Unable to read file', 'warning')
            print(str(e))
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
        self.gui_plot.clear_plots()
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

            # Checks if the cut is done on the first third of the dataset, which would be considered
            # a cut on the beginning of the data.
            if index < len(self.mdata[ind]['temp'])/3:
                for i in range(len(self.mdata[ind]['temp'][:index])):
                    self.mdata[ind]['temp'][i] = 999
            else:
                for i in range(1, len(self.mdata[ind]['temp'][index:])):
                    self.mdata[ind]['temp'][i + index] = 999
        except ValueError:
            self.console_writer('Select value that is not the start or ending', 'warning')
            return

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
            # Sets the x axis on the top
            self.plot.xaxis.tick_top()

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', self.mdata[0]['region'], True)
        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError:
            self.console_writer('Load more than a file for the Hovmoller Diagram', 'warning')

    def plot_stratification(self):
        """
        Method: plot_stratification(self)
        Purpose: Plots the stratification plot from May to December of a given year with the historical file
        Require:
        Version: 04/2022, MJB: Documentation
        """

        historical = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()

        df, hismintemp, hismaxtemp, bad = fm.historic_to_df(historical, year)
        try:
            global cb
            self.clear_plots()
            self.counter.append("Stratification")
            depths = np.array(list(map(float, list(df.columns))))
            if self.plot1.axes:
                plt.Axes.remove(self.plot1)
                plt.Axes.remove(self.plot2)
            self.plot = self.fig.add_subplot(111)

            if depths[-1] < 40:
                self.plot.set_ylim(0, -40)
                self.plot.set_yticks(-np.insert(depths, [0, -1], [0, 40]))
            else:
                self.plot.set_ylim(0, -depths[-1])
                self.plot.set_yticks(-np.insert(depths, 0, 0))

            self.plot.set_xlim(datetime.strptime('01/05/' + year + ' 00:00:00', '%d/%m/%Y %H:%M:%S'),
                               datetime.strptime('01/12/' + year + ' 00:00:00', '%d/%m/%Y %H:%M:%S'))
            # self.plot.set_xlim(pd.to_datetime(df.index[0]), pd.to_datetime(df.index[-1]))

            # self.plot.set_yticks(-np.arange(0, depths[-1]+1, 5))
            self.plot.invert_yaxis()
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
            '''
            if hismaxtemp < round(np.nanmax(dfcopy.quantile(0.99))) + 1:
                hismaxtemp = round(np.nanmax(dfcopy.quantile(0.99))) + 1
            if hismintemp > np.round(np.nanmin(dfcopy.quantile(0.01))) - 1:
                hismintemp = round(np.nanmin(dfcopy.quantile(0.01))) - 1
            '''
            levels = np.arange(np.floor(hismintemp), hismaxtemp, 1)
            levels2 = np.arange(np.floor(hismintemp), hismaxtemp, 0.1)


            # Draws a contourn line.
            # ct = self.plot.contour(df.index.to_pydatetime(), -depths, df.values.T, colors='black', linewidths=0.5)
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
                    cf.append(self.plot.contourf(pd.to_datetime(df_cuts[i].index), -depths, df_cuts[i].values.T, 256,
                                                 extend='both',
                                                 cmap='RdYlBu_r', levels=levels2))
                cb = plt.colorbar(cf[0], ax=self.plot, label='Temperature (ºC)', ticks=levels)
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
                        cf = self.plot.contourf(df_datetime, -depths[old_index: i + 1],
                                                df.filter(items=str_depths[old_index:i + 1]).values.T, 256, extend='both',
                                                cmap='RdYlBu_r',
                                                levels=levels2)
                        old_index = i + 1
                    cf = self.plot.contourf(df_datetime, -depths[old_index:],
                                            df.filter(items=str_depths[old_index:]).values.T, 256, extend='both',
                                            cmap='RdYlBu_r',
                                            levels=levels2)
                else:
                    cf = self.plot.contourf(df_datetime, -depths, df.values.T, 256, extend='both', cmap='RdYlBu_r',
                                            levels=levels2)

                cb = plt.colorbar(cf, ax=self.plot, label='Temperature (ºC)', ticks=levels)
            self.cbexists = True
            self.plot.set(ylabel='Depth (m)',
                          title=historical.split('_')[4] + ' year ' + year)
            self.savefilename = historical.split('_')[3] + '_1_' + year + '_' + historical.split('_')[4]
            # Sets the X axis as the initials of the months
            locator = mdates.MonthLocator()
            self.plot.xaxis.set_major_locator(locator)
            fmt = mdates.DateFormatter('%b')
            self.plot.xaxis.set_major_formatter(fmt)
            # Sets the x axis on the top
            self.plot.xaxis.tick_top()
            # Sets the ticks only for the whole depths, the ones from the file
            tick_depths = [-i for i in depths if i.is_integer()]
            self.plot.set_yticks(tick_depths)

            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', historical.split('_')[3], True)
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
        year = self.secondInput.get()

        self.newwindow.destroy()
        self.clear_plots()
        self.counter.append("Cycles")

        '''
        excel_object = fw.Excel(historical, write_excel=False, seasonal=False)  # returns an excel object
        histdf = excel_object.monthlymeandf
        '''
        histdf = pd.read_csv(historical, sep='\t')
        depths = histdf.columns[2:]
        histdf['day'] = pd.DatetimeIndex(histdf['Date'], dayfirst=True).day
        histdf['month'] = pd.DatetimeIndex(histdf['Date'], dayfirst=True).month
        histdf['day_month'] = histdf['day'].astype(str) + '-' + histdf['month'].astype(str)
        histdf['day_month'] = histdf['day_month'] +'-' + year
        histdf['day_month'] = pd.DatetimeIndex(histdf['day_month'], dayfirst=True)

        orderedhist_df = histdf.groupby('day_month')[depths].mean()
        orderedhist_df.sort_index(inplace=True)

        year_df, hismintemp, hismaxtemp, minyear = fm.historic_to_df(historical, year, start_month='01', end_month='01')
        year_df.index = year_df.index.strftime('%Y-%m-%d %H:%M:%S')
        if '0' in year_df.columns:
            year_df.drop('0', axis=1, inplace=True)


        year_df = fm.running_average_special(year_df, running=360)
        orderedhist_df = fm.running_average_special(orderedhist_df, running=15)
        orderedhist_df.index = pd.DatetimeIndex(orderedhist_df.index)
        # dfdelta = fm.running_average(self.mdata, running=360)

        # All this block serves only to transform the data from hourly to daily. It should be inside its own method
        daylist = []
        # Converts the index from timestamp to string
        '''
        for time in year_df.index:
            old = datetime.strftime(time, '%Y-%m-%d')
            new = datetime.strptime(old, '%Y-%m-%d')
            
            daylist.append(new)
        dfdelta['day'] = daylist
        '''
        daylist = []
        for time in year_df.index:
            if str(time) == 'nan':
                pass
            else:
                old = datetime.strftime(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d')
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

        # TODO Why the filter does not look the same? ASk Nathaniel
        # TODO change the x axis to reflect the name of the month

        '''
        # Dict to change from string months to datetime

        monthDict = {}
        for i in range(1, 13):
            if i < 10:
                monthDict['0' + str(i)] = datetime.strptime(year + '-0' + str(i) + '-01',
                                                            '%Y-%m-%d')
                # monthDict['0'+str(i)] = datetime.strptime(datetime.strftime(dfdelta.index[0], '%Y')+'-0' + str(i) + '-01',                                                          '%Y-%m-%d')
            else:
                monthDict[str(i)] = datetime.strptime(year + '-' + str(i) + '-01',
                                                      '%Y-%m-%d')
                # monthDict[str(i)] = datetime.strptime(datetime.strftime(dfdelta.index[0], '%Y') + '-' + str(i) + '-01', '%Y-%m-%d')
        '''
        # Creates the subplots and deletes the old plot
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)

        self.plot = self.fig.add_subplot(111)
        '''
        for month in histdf['month'].unique():
            histdf['month'].replace(month, monthDict[month], inplace=True)
        
        usedf = histdf.copy()
        usedf.set_index('month', inplace=True)
        usedf.sort_index(inplace=True)
        
        if str(minyear) != year:
            oldepth = 0
            for depth in usedf['depth'].unique():
                if oldepth != 0:

                    self.plot.fill_between(np.unique(usedf.index), usedf.loc[usedf['depth'] == oldepth]['mean'],
                                           usedf.loc[usedf['depth'] == depth]['mean'], facecolor='lightgrey', zorder=0)

                oldepth = depth
        '''



        color_dict = {'5': '#d4261d', '10': '#f58e6e', '15': '#fca95a', '20': '#fde5a3', '25': '#e4f4f8',
                      '30': '#a7d6e7',
                      '35': '#9ec6de', '40': '#3a6daf', '45': '#214f8a', '50': '#0a3164'}
        # Checks if there is empty depths to delete them and make them not show on the legend
        for depth in newdf.columns:
            if newdf[depth].isnull().all():
                del newdf[depth]
        newdf.plot(ax=self.plot, zorder=10, color=[color_dict.get(x, '#333333') for x in newdf.columns])

        leg = self.plot.legend(title='Depth (m)')

        if str(minyear) != year:
            oldepth = 0
            for depth in orderedhist_df.columns:
                if oldepth != 0:
                    self.plot.fill_between(np.unique(orderedhist_df.index), orderedhist_df[oldepth],
                                           orderedhist_df[depth], facecolor='lightgrey', zorder=0)
                oldepth = depth
                orderedhist_df.plot(kind='line', ax=self.plot, color='#e9e8e8', label='_nolegend_', legend=False, zorder=5)

        '''
        if str(minyear) != year:
            for depth in usedf['depth'].unique():
                histdf['depth'] = histdf['depth'].astype('int')
                histdf.sort_values(['month', 'depth'], inplace=True)
                histdf['depth'] = histdf['depth'].astype('str')
                histdf.loc[histdf['depth'] == depth].plot(kind='line', x='month', y='mean', ax=self.plot, color='#e9e8e8',
                                                          label='_nolegend_', legend=False, zorder=5)
        '''
        self.plot.set(ylabel='Temperature (ºC) smoothed',
                      title=historical.split('_')[4] + ' year ' + year)
        self.plot.set_yticks(np.arange(10, hismaxtemp, 2))  # Sets the limits for the Y axis
        self.plot.set_xlim([year + '-01-01' + ' 00:00:00', str(int(year) + 1) + '-01-01' + ' 00:00:00'])

        self.savefilename = historical.split('_')[3] + '_2_' + year + '_' + historical.split('_')[4]

        # Sets the X axis as the initials of the months
        locator = mdates.MonthLocator()
        self.plot.xaxis.set_major_locator(locator)
        fmt = mdates.DateFormatter('%b')
        self.plot.xaxis.set_major_formatter(fmt)

        self.plot.xaxis.set_label_text('foo').set_visible(False)
        # fig.set_size_inches(14.5, 10.5, forward=True)

        self.plot.text(0.1, 0.1, "multi-year mean", backgroundcolor='grey')
        self.canvas.draw()

    def plot_thresholds(self):
        """
       Method: plot_thresholds(self)
       Purpose: Creates the thresholds graph
       Require:
       Criteria: 
       Version: 11/2021, MJB: Documentation
       """
        historical = self.openfileinput.get()
        # Deprecating region input as it can be gotten automatically from the filename (self.mdata[0]['region_name'])
        # region = self.regioninput.get()
        self.newwindow.destroy()
        self.clear_plots()
        self.counter.append("Thresholds")
        excel_object = fw.Excel(historical, write_excel=False, console=self.consolescreen)  # returns an excel object
        df = excel_object.mydf3

        # Converts Number of operation days [N] = 0 to np.nan
        df['N'].replace(0, np.nan, inplace=True)

        dfhist_control = pd.read_csv(historical, sep='\t', dayfirst=True)
        dfhist_control['Date'] = pd.to_datetime(dfhist_control['Date'])
        dfhist_control['year'] = pd.DatetimeIndex(dfhist_control['Date']).year
        dfhist_control['month'] = pd.DatetimeIndex(dfhist_control['Date']).month
        dfhist_summer = dfhist_control.loc[
            (dfhist_control['month'] == 7) | (dfhist_control['month'] == 8) | (
                        dfhist_control['month'] == 9)]

        # Check if any depth is all nan which means there are no data for said depth
        depths = df['depth(m)'].unique()

        for depth in depths:
            for year in df['year'].unique():
                if (dfhist_summer.loc[dfhist_summer['year'] == int(year)][depth].isnull().all()) | (dfhist_summer.loc[dfhist_summer['year'] == int(year)][depth].count() / 24 < 30):
                    for i in range(23, 29):
                        df.loc[(df['year'] == str(year)) & (df['depth(m)'] == depth), 'Ndays>=' + str(i)] = np.nan
                else:
                    print('not all na')





        # Creates the subplots and deletes the old plot
        if self.plot1.axes:
            plt.Axes.remove(self.plot1)
            plt.Axes.remove(self.plot2)
        self.plot = self.fig.add_subplot(111)

        # TODO matplotlib no tiene los mismos markers que matlab, se comprometen los 3 ultimos

        # TODO esto se puede cambiar por un Cycler y entonces no dependeria del trozo de codigo extraño de más abajo
        # Setting the properties of the line as lists to be used on a for loop depending on the year
        markers = ['+', 'o', 'x', 's', 'd', '^', 'v', 'p', 'h', '*']
        colors = ['b', 'b', 'k', 'k']
        lines = ['solid', 'dotted', 'solid', 'dotted']

        # Loop to decide each year which style has
        # TODO check code in 2030 to change this method
        # We get all the years on the dataset
        years = df['year'].unique()
        years = years[years != 0]

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
            '''
            for ni in df.loc[df['year'] == year].index:
                if ni != df.loc[df['year'] == year].index[-1]:
                    if df['N'][ni] != 0 and df['N'][ni] < df['N'][ni + 1] - 240:
                        df['N'][ni] = np.nan
                        for j in range(23, 29):
                            df['Ndays>=' + str(j)][ni] = np.nan
            '''
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
            self.plot.set(ylim=(0, maxdepth + 2))
            if maxdays >= 30:
                ticks = 10
            elif maxdays >=20:
                ticks = 5
            else:
                ticks = 2
            self.plot.set(xlim=(-2, maxdays + 2), xticks=np.arange(0, maxdays + 2, ticks))
            # Remove asterisks (if any) on years
            seq_type = type(year)
            int_year = int(seq_type().join(filter(seq_type.isdigit, year)))
            if int_year < 2000:
                color = colors[0]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 1990]
                               , color=color, linestyle=lines[0])
            elif int_year >= 2000 and int_year < 2010:
                color = colors[1]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2000],
                               color=color, linestyle=lines[1])
            elif int_year >= 2010 and int_year < 2020:
                color = colors[2]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2010],
                               color=color, linestyle=lines[2])
            elif int_year >= 2020 and int_year < 2030:
                color = colors[3]
                if year == years[-1]:
                    color = 'tab:orange'
                self.plot.plot(year_dict[year][23][:, 0], year_dict[year][23][:, 1], marker=markers[int_year - 2020],
                               color=color, linestyle=lines[3])

            self.plot.invert_yaxis()
            self.plot.xaxis.tick_top()
            self.canvas.draw()
        # Shrink the axis a bit to fit the legend outside of it
        box = self.plot.get_position()
        self.plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # Draws the legend for the different years
        legend = self.plot.legend(legend_years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
        self.plot.set(ylabel='Depth (m)',
                      title=historical.split('_')[4] + ' Summer (JAS) days ≥ 23ºC')
        self.plot.xaxis.grid(True, linestyle='dashed')

        p = self.plot.get_window_extent()
        self.plot.annotate('*Recorded period not complete', xy=(0.68, 0.03), xycoords=p, xytext=(0.1, 0), textcoords="offset points",
                  va="center", ha="left",
                  bbox=dict(boxstyle="round", fc="w"))

        self.canvas.draw()
        # Adds tabs for the temperatures being buttons to call raiseTab and plot the Thresholds
        for i in range(23, 29):
            tab = {}
            btn = tk.Button(self.toolbar, text=i,
                            command=lambda i=i, maxdepth=maxdepth, maxdays=maxdays: self.raiseTab(i, maxdepth,
                                                                                                  year_dict, markers,
                                                                                                  colors, lines, years,
                                                                                                  maxdays, historical, legend_years))
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
            tab['id'] = i
            tab['btn'] = btn
            self.tabs[i] = tab
        self.curtab = 23
        print('Ayo')
        self.savefilename = historical.split('_')[3] + '_3_23_' + year + '_' + historical.split('_')[4]

    def raiseTab(self, i, maxdepth, year_dict, markers, colors, lines, years, maxdays, historical, legend_years):
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
            if maxdays >= 30:
                ticks = 10
            elif maxdays >=20:
                ticks = 5
            else:
                ticks = 2
            self.plot.set(ylim=(0, maxdepth + 2))
            self.plot.set(xlim=(-2, maxdays + 2), xticks=np.arange(0, maxdays + 2, ticks))
            for year in years:
                # Remove asterisks (if any) on years
                seq_type = type(year)
                int_year = int(seq_type().join(filter(seq_type.isdigit, year)))
                if int_year < 2000:
                    color = colors[0]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 1990]
                                   , color=color, linestyle=lines[0])
                elif int_year >= 2000 and int_year < 2010:
                    color = colors[1]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2000],
                                   color=color, linestyle=lines[1])
                elif int_year >= 2010 and int_year < 2020:
                    color = colors[2]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2010],
                                   color=color, linestyle=lines[2])
                elif int_year >= 2020 and int_year < 2030:
                    color = colors[3]
                    if year == years[-1]:
                        color = 'tab:orange'
                    self.plot.plot(year_dict[year][i][:, 0], year_dict[year][i][:, 1], marker=markers[int_year - 2020],
                                   color=color, linestyle=lines[3])

            self.plot.invert_yaxis()
            self.plot.xaxis.tick_top()
            # Shrink the axis a bit to fit the legend outside of it
            box = self.plot.get_position()
            self.plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            legend = self.plot.legend(legend_years, title='Year', loc='center left', bbox_to_anchor=(1, 0.5))
            self.plot.set(ylabel='Depth (m)',
                          title=historical.split('_')[4] + ' Summer(JAS) days ≥ ' + str(i) + 'ºC')
            self.savefilename = historical.split('_')[3] + '_3_' + str(i) + '_' + year + '_' + historical.split('_')[4]

            p = legend.get_window_extent()
            self.plot.annotate('*Recorded period not complete', xy=(0, -0.1), xycoords=p, xytext=(0.1, 0),
                               textcoords="offset points",
                               va="center", ha="left",
                               bbox=dict(boxstyle="round", fc="w"))
            self.plot.xaxis.grid(True, linestyle='dashed')
            self.canvas.draw()

        self.curtab = i
        self.console_writer("Plotting for over " + str(i) + " degrees", "action")

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
                    filename = self.savefilename
                elif self.counter[0] == 'Thresholds':
                    filename = self.savefilename
                elif self.counter[0] == 'Filter':
                    filename = str(self.value[:-7]) + " filtered differences"
                elif self.counter[0] == 'Difference':
                    filename = str(self.value[:-7]) + " differences"
                elif self.counter[0] == 'Stratification':
                    filename = self.savefilename
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
                self.mdata[0]['images'].append(
                    file)  # Stores the path of the created images to print them on the report
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
        duplicity = fw.big_merge(filename1, filename2, output)
        if len(duplicity) > 0:
            self.console_writer('Found duplicity between '
                                + str(len(duplicity)) + ' dates. First occurrence at '
                                + str(duplicity[0]) + ' last at ' + str(duplicity[-1]), 'warning')


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
        #output = self.secondInput.get()
        self.newwindow.destroy()
        # fw.Excel(input, '../src/output_files/' + output + '.xlsx')
        ew.excel_writer(input)
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

    def window_browser(self, title, cmd, label1, label2=None):
        self.newwindow = Toplevel()
        self.newwindow.title(title)

        Label(self.newwindow, text=label1).grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        Button(self.newwindow, text='Browse', command=self.browse_file).grid(row=0, column=2)

        if label2:
            Label(self.newwindow, text=label2).grid(row=1, pady=10)
            self.secondInput = Entry(self.newwindow, width=20)
            self.secondInput.grid(row=1, column=1)
            Button(self.newwindow, text='Select', command=cmd).grid(row=2, column=1)
        else:
            Button(self.newwindow, text='Select', command=cmd).grid(row=1, column=1)

    def generate_netCDF(self):
        filename = self.openfileinput.get()
        self.newwindow.destroy()
        df = pd.read_csv(filename, sep='\t')
        fm.convert_to_netCDF('finalCDM', df, self.consolescreen)

    def create_heat_spikes(self):
        filename = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        historic = st.HistoricData(filename)
        for i in range(int(year), historic.last_year):
            historic.browse_heat_spikes(i)
        self.console_writer('Plots saved at output_images', 'action')

    def create_anomalies(self):
        filename = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        historic = st.HistoricData(filename)
        for i in range(int(year), historic.last_year):
            historic.browse_anomalies(i)
        self.console_writer('Plots saved at output_images', 'action')

    def create_tridepth_anomalies(self):
        filename = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        historic = st.HistoricData(filename)
        for i in range(int(year), historic.last_year):
            historic.multidepth_anomaly_plotter(i)
        self.console_writer('Plots saved at output_images', 'action')

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
