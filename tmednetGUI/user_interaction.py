import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename, asksaveasfilename, askdirectory
from tkinter import messagebox, Button
from tkinter import scrolledtext
from PIL import Image, ImageTk
import pandas as pd
import time

import file_manipulation as fm
import matplotlib
import numpy as np

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as dates

from datetime import timedelta

version = "0.5"
build = "April 2021"


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
        filemenu.add_command(label="Exit", command=lambda: close(self))
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="To UTC", command=self.to_utc)
        editmenu.add_command(label="Get original data", command=self.go_back)
        editmenu.add_command(label="Merge Files", command=self.merge)
        editmenu.add_command(label="Cut Endings", command=self.cut_endings)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.master.config(menu=menubar)

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
        toolbar = NavigationToolbar2Tk(self.canvas, f2)
        toolbar.children['!button5'].pack_forget()
        tk.Button(toolbar, text="Clear Plot", command=self.clear_plots).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=0)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar.update()

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
        if self.cbexists:
            self.clear_plots()

        # if self.plotcb.axes:
        #  plt.Axes.remove(self.plotcb)

        masked_ending_temperatures = np.ma.masked_where(np.array(self.mdata[index]['temp']) == 999,
                                                        np.array(self.mdata[index]['temp']))
        if self.plot.axes:
            # self.plot = self.fig.add_subplot(111)
            self.plot.plot(self.mdata[index]['timegmt'], masked_ending_temperatures,
                           '-', label=str(self.mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title='Multiple depths at Region: ' + str(self.mdata[index]['region']))
        else:
            self.plot = self.fig.add_subplot(111)
            self.plot.plot(self.mdata[index]['timegmt'], masked_ending_temperatures,
                           '-', label=str(self.mdata[index]['depth']))
            self.plot.set(ylabel='Temperature (DEG C)',
                          title=self.files[index] + "\n" + 'Depth:' + str(
                              self.mdata[index]['depth']) + " - Region: " + str(
                              self.mdata[index]['region']))

        self.plot.legend()
        # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_zoom(self):
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
        time_series, temperatures, indexes, start_index = fm.zoom_data(self.mdata[index])

        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        masked_ending_temperatures = np.ma.masked_where(np.array(temperatures[1][int(indexes[0]):]) == 999,
                                                        np.array(temperatures[1][int(indexes[0]):]))

        self.plot1.plot(time_series[0][int(start_index):], temperatures[0][int(start_index):],
                        '-', color='steelblue', marker='o', label=str(self.mdata[index]['depth']))
        self.plot1.legend()
        self.plot1.plot(time_series[0][:int(start_index) + 1], temperatures[0][:int(start_index) + 1],
                        '-', color='red', marker='o', label=str(self.mdata[index]['depth']))

        self.plot1.set(ylabel='Temperature (DEG C)',
                       title=self.files[index] + "\n" + 'Depth:' + str(
                           self.mdata[index]['depth']) + " - Region: " + str(
                           self.mdata[index]['region']))

        self.plot2.plot(time_series[1][:int(indexes[0] + 1)], temperatures[1][:int(indexes[0]) + 1],
                        '-', color='steelblue', marker='o', label=str(self.mdata[index]['depth']))
        self.plot2.legend()
        # Plots in the same graph the last part which represents the errors in the data from removing the sensors
        self.plot2.plot(time_series[1][int(indexes[0]):], masked_ending_temperatures,
                        '-', color='red', marker='o', label=str(self.mdata[index]['depth']))
        self.plot2.set(ylabel='Temperature (DEG C)',
                       title=self.files[index] + "\n" + 'Depth:' + str(
                           self.mdata[index]['depth']) + " - Region: " + str(
                           self.mdata[index]['region']))

        # fig.set_size_inches(14.5, 10.5, forward=True)
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
        for i in range(len(self.mdata[ind]['temp'][index:])):
            self.mdata[ind]['temp'][i + index] = 999
        self.plot_zoom()


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
        depths = ""
        # Creates the subplots and deletes the old plot
        if not self.plot1.axes:
            self.plot1 = self.fig.add_subplot(211)
            self.plot2 = self.fig.add_subplot(212)

        for i in index:
            time_series, temperatures, _, bad = fm.zoom_data(self.mdata[i])
            depths = depths + " " + str(self.mdata[i]['depth'])

            masked_ending_temperatures = np.ma.masked_where(np.array(temperatures[1]) == 999,
                                                            np.array(temperatures[1]))
            self.plot1.plot(time_series[0], temperatures[0],
                            '-', label=str(self.mdata[i]['depth']))
            self.plot1.set(ylabel='Temperature (DEG C)',
                           title='Temperature at depths:' + depths + " - Region: " + str(
                               self.mdata[i]['region']))
            self.plot1.legend()

            self.plot2.plot(time_series[1], masked_ending_temperatures,
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

            cb = plt.colorbar(cf, ax=self.plot, label='temperature', ticks=levels)
            self.cbexists = True
            self.plot.set(ylabel='Depth (m)',
                          title='Hovmoller Diagram')
            self.canvas.draw()

            self.console_writer('Plotting the HOVMOLLER DIAGRAM at region: ', 'action', self.mdata[0]['region'], True)
        except IndexError:
            self.console_writer('Load several files before creating a diagram', 'warning')
        except TypeError:
            self.console_writer('Load more than a file for the Hovmoller Diagram', 'warning')

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
                    self.mdata[i]['temp'] = self.tempdataold[i].copy()
                self.recoverindex = None
                # self.tempdataold = None
            else:
                i = 0
                for data in self.mdata:
                    data['temp'] = self.tempdataold[i].copy()
                    i += 1
            self.console_writer('Recovering old data', 'action')
            self.clear_plots()
        except (AttributeError, TypeError):
            self.console_writer('Cut the ending of a file before trying to recover it', 'warning')

    def clear_plots(self):
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
                _, temperatures, indexes, bad = fm.zoom_data(data)
                for i in indexes:
                    data['temp'][int(i) - len(np.array(temperatures[1]))] = 999
            self.console_writer('Endings of all the files cut', 'action', liner=True)
            self.reportlogger.append('Endings automatically cut')
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

            if len(self.counter) == 1:  # Writes the default name of the image file according to the original file
                filename = self.value[:-4]
            if len(self.counter) > 1:
                filename = ""
                for n in self.counter:
                    filename = filename + "_" + self.files[n][-6:-4]
                filename = self.mdata[0]["datainici"].strftime("%Y-%m-%d") + "_" \
                           + self.mdata[0]["datafin"].strftime("%Y-%m-%d") + "_Combo of depths" + filename

            file = asksaveasfilename(initialdir='../src/output_images',
                                     filetypes=(("PNG Image", "*.png"), ("JPG Image", "*.jpg"), ("All Files", "*.*")),
                                     defaultextension='.png', initialfile=filename, title="Save as")
            if file:
                self.fig.savefig(file)
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
