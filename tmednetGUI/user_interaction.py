import sys
import time
import matplotlib
import GUI_plots as gp
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
import file_writer as fw
import excel_writer as ew
import tkinter.font as tkFont
import surface_temperature as st
from PIL import Image, ImageTk
from datetime import timedelta
import matplotlib.dates as dates
from tkinter import messagebox, Button
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

version = "0.8"
build = "Mars 2022"
matplotlib.use("TkAgg")

import data_manager as fm2
class tmednet(tk.Frame):
    """
    Creates the GUI. This class will be the only direct interaction the user will have
    with all of the code. All the complex calculations and different manipulations
    that occur due to the user input happen in another classes.

    ...

    Attributes
    ----------
    master : tk Frame
        The main frame of the GUI
    gui_plot : GUIPlot object
        Object containing all the information necessary to create the different plots that will
        be shown on the GUI
    dm : DataManager object
        Object containing all the data that is being loaded into the GUI.
        It also allows to load and manipulate said data.
    toolbar : NavigationToolbar2Tk
        Object that contains the plot manipulation buttons
    list : Listbox
        Object that contains the loaded files filenames
    right_menu : Menu
        Object that contains the menu buttons that pop up when right clicking on the list box
    textBox : tk Text
        Object that contains a black box in which the report is written
    consolescreen : tk text
        Object that contains a black box in which all the console messages are written
    recoverindex : list
        List containing the index of the files that have been cut manually
    reportlogger : list
        List containing the strings of the important changes to be stored on the report

    Methods
    -------
    console_writer(self, msg, mod, var=False, liner=False)
        Writes messages on the console
    on_open(self)
        Launches the askopen widget to set data filenames through the DataManager object
    reset(self)
        Reset the attributes and clear the lists, plots, console and report windows
    cut_data_manually(self, event, ind)
        Event controller to cut the data by selecting the points directly on the plot
    plot_stratification(self)
        Calls the method on GUIPlot object to plot the stratification
    plot_annualTCycle(self)
        Calls the method on GUIPlot object to plot the annual T Cycle
    plot_thresholds(self)
        Calls the method on GUIPlot object to plot the thresholds
    go_back(self)
        Returns to the original data, before applying any cuts
    cut_endings(self)
        Cuts the endings of the data that is considered 'not real' (using the DataManager
        method zoom_data)
    on_save(self)
        Saves the file with a proposed name and lets the user choose one of their liking.
    merge(self)
        Merges all of the loaded files into a single geojson and txt one
    write_excel(self)
        Informs the report and launches the write_excel function
    help()
        Shows an about message
    close(self)
        Quits and closes the GUI
    """

    def __init__(self, master=None):
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
        self.__init_variables()

        # We build the GUI
        self.__init_window()

    def __init_window(self):
        # Builds the GUI
        menubar = tk.Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.on_open)
        filemenu.add_command(label="Save", command=self.on_save)
        filemenu.add_command(label="Report", command=lambda: self.dm.report(self.textBox))
        filemenu.add_separator()
        filemenu.add_command(label="Reset", command=self.reset)
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Get original data", command=self.go_back)
        editmenu.add_command(label="Merge Files", command=self.merge)
        editmenu.add_command(label="Cut Endings", command=self.cut_endings)
        menubar.add_cascade(label="Edit", menu=editmenu)

        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Historical Merge', command=self.__historical_merge_window)
        toolsmenu.add_command(label='Create Excel',
                              command=lambda: self.__window_browser('Select file and output file name',
                                                                  self.write_excel, 'Input: '))
        toolsmenu.add_command(label='Create netCDF',
                              command=lambda: self.__window_browser('Select historical file',
                                                                  self.__generate_netCDF, 'Historical: '))
        toolsmenu.add_command(label='Create Heat spikes',
                              command=lambda: self.__window_browser('Select historical file',
                                                                  self.__create_heat_spikes, 'Historical: ', 'Year'))
        toolsmenu.add_command(label='Create anomalies',
                              command=lambda: self.__window_browser('Select historical file',
                                                                  self.__create_anomalies, 'Historical: ', 'Year'))
        toolsmenu.add_command(label='Create tridepth anomalies',
                              command=lambda: self.__window_browser('Select historical file',
                                                                  self.__create_tridepth_anomalies, 'Historical: ', 'Year'))
        menubar.add_cascade(label='Tools', menu=toolsmenu)

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
        self.gui_plot = gp.GUIPlot(f2, self.console_writer, self.reportlogger, self.dm)
        self.toolbar = NavigationToolbar2Tk(self.gui_plot.canvas, f2)
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
        self.list.bind("<<ListboxSelect>>", self.__select_list)

        self.right_menu = Menu(frame1, tearoff=0)
        self.right_menu.add_command(label="Zoom", command=lambda: self.gui_plot.plot_zoom(self.dm.mdata, self.dm.files, self.list, self.cut_data_manually))
        self.right_menu.add_command(label="Zoom all files", command=lambda: self.gui_plot.plot_all_zoom(self.dm.mdata, self.list))  # Placeholders
        self.right_menu.add_command(label="Plot difference", command=self.gui_plot.plot_dif)
        self.right_menu.add_command(label="Plot filter", command=self.gui_plot.plot_dif_filter1d)
        self.right_menu.add_separator()
        self.right_menu.add_command(label="Plot Hovmoller", command=lambda: self.gui_plot.plot_hovmoller(self.dm.mdata))
        self.right_menu.add_command(label="Plot Stratification",
                                    command=lambda: self.__window_browser('Select historical file and year',
                                                                        self.plot_stratification, 'Historical: ',
                                                                        'Year: '))
        self.right_menu.add_command(label="Plot Annual T Cycles",
                                    command=lambda: self.__window_browser('Select historical file and year',
                                                                        self.plot_annualTCycle, 'Historical: ',
                                                                        'Year: '))
        self.right_menu.add_command(label="Plot Thresholds",
                                    command=lambda: self.__window_browser('Select historical file',
                                                                        self.plot_thresholds, 'Historical: '))

        self.list.bind("<Button-3>", self.__do_popup)
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

    def __init_variables(self):
        # Initializes the variables
        self.recoverindex = None
        self.reportlogger = []
        self.dm = fm2.DataManager(self.console_writer, self.reportlogger)

    def console_writer(self, msg, mod='action', var=False, liner=False):
        """
        Writes messages to the console

        ...

        Parameters
        ----------
        msg : str
            The message that the console will output
        mod : str, optional
            Modifier for the message (if it is a warning, an action...)
            (Default action)
        var : str, optional
            If there is an additional variable to be added to the message
            (Default False)
        liner : bool, optional
            Controls when to end the message with '==='
            (Default False)
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

    def __do_popup(self, event):
        # Event controller to raise a right click menu
        try:
            self.right_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_menu.grab_release()

    def __select_list(self, evt):
        # Event handler for when an item of the list is selected
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
                self.gui_plot.plot_ts(self.dm.mdata, self.dm.files, index)

        except IndexError as e:
            print(e)  # Not knowing why this error raises when Saving the file but doesn't affect the code. Should check.
            
    def on_open(self):
        """
        Launches the askopen widget to set data filenames through the DataManager object
        """
        files = askopenfilenames(initialdir='../src', title="Open files",
                                 filetypes=[("All files", "*.*")])
        try:
            filesname = self.dm.openfile(files, self.textBox, self.list)
            for file in filesname:  # Itera toda la lista de archivos para añadirlos a la listbox
                self.dm.files.append(file)
            self.dm.load_data()
        except TypeError as e:
            self.console_writer('Unable to read file', 'warning')
            print(str(e))
        return

    def reset(self):
        """
        Reset the parameters and clear the lists, plots, console and report windows
        """
        self.gui_plot.clear_plots()
        self.list.delete(0, END)
        self.textBox.delete('1.0', END)
        self.consolescreen.delete('1.0', END)
        self.__init_variables()

    def cut_data_manually(self, event, ind):
        """
        Event controller to cut the data by selecting the points directly on the plot
        
        ...
        
        Parameters
        ----------
        event : button press event
            Place that was clicked
        ind : int
            Index of the file of the list that is being modified
        """
        # TODO Fix a bug that duplicates the event handler click when using the Go_Back function
        try:
            xtime = dates.num2date(event.xdata)
            xtime_rounded = xtime.replace(second=0, microsecond=0, minute=0, hour=xtime.hour) + timedelta(
                hours=xtime.minute // 30)
            xtime_rounded = xtime_rounded.replace(tzinfo=None)
            index = int(self.dm.mdata[0]['df'].index.get_indexer([xtime_rounded]))
            print('Cutting data')
            self.console_writer('Cutting data at depth: ', 'action', self.dm.mdata[ind]['depth'])
            self.console_writer(' at site ', 'action', self.dm.mdata[ind]['region'], True)

            if self.recoverindex:
                self.recoverindex.append(ind)
            else:
                self.recoverindex = [ind]

            # Checks if the cut is done on the first third of the dataset, which would be considered
            # a cut on the beginning of the data.
            if index < len(self.dm.mdata[ind]['df'])/3:
                for i in range(len(self.dm.mdata[ind]['df'][:index])):
                    self.dm.mdata[ind]['df']['Temp'][i] = 999
            else:
                for i in range(1, len(self.dm.mdata[ind]['df'][index:])):
                    self.dm.mdata[ind]['df']['Temp'][i + index] = 999
        except ValueError:
            self.console_writer('Select value that is not the start or ending', 'warning')
            return

    def plot_stratification(self):
        """
        Calls the method on GUIPlot object to plot the stratification
        """
        historical = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        self.gui_plot.plot_stratification(historical, year)

    def plot_annualTCycle(self):
        """
        Calls the method on GUIPlot object to plot the annual T Cycle
        """

        # Gets the historical data to calculate the multi-year mean and deletes the old plots
        historical = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        self.gui_plot.plot_annual_T_cycle(historical, year)

    def plot_thresholds(self):
        """
        Calls the method on GUIPlot object to plot the thresholds
        """
        historical = self.openfileinput.get()
        self.newwindow.destroy()
        self.gui_plot.plot_thresholds(historical, self.toolbar, self.consolescreen)

    def go_back(self):
        """
        Returns to the original data, before applying any cuts
        """
        try:
            if self.recoverindex:
                for i in self.recoverindex:
                    self.dm.mdata[i]['df'] = self.dm.tempdataold[i]['df'].copy()
                self.recoverindex = None

            else:
                i = 0
                for data in self.dm.mdata:
                    data['df'] = self.dm.tempdataold[i]['df'].copy()
                    i += 1
            self.console_writer('Recovering old data', 'action')
            self.gui_plot.clear_plots()
        except (AttributeError, TypeError):
            self.console_writer('Cut the ending of a file before trying to recover it', 'warning')

    def cut_endings(self):
        """
        Cuts the endings of the data that is considered 'not real' (using the DataManager
        method zoom_data)
        """
        if self.dm.mdata:
            self.dm.zoom_data_loop()
            self.console_writer('Endings of all the files cut', 'action', liner=True)
            self.reportlogger.append('Endings and start automatically cut')
        else:
            self.console_writer('Load a file before trying to cut it', 'warning')

    def on_save(self):
        """
        Saves the file with a proposed name and lets the user choose one of their liking.
        """
        try:  # If there is no plot, it shows an error message
            if self.gui_plot.counter[-1] == 'Zoom':
                zoom = self.gui_plot.counter.pop()
            else:
                zoom = ''
            if len(self.gui_plot.counter) == 1:  # Writes the default name of the image file according to the original file
                if self.gui_plot.counter[0] == "Hovmoller":
                    filename = str(self.value[:-7]) + " Hovmoller"
                elif self.gui_plot.counter[0] == 'Cycles':
                    filename = self.gui_plot.savefilename
                elif self.gui_plot.counter[0] == 'Thresholds':
                    filename = self.gui_plot.savefilename
                elif self.gui_plot.counter[0] == 'Filter':
                    filename = str(self.value[:-7]) + " filtered differences"
                elif self.gui_plot.counter[0] == 'Difference':
                    filename = str(self.value[:-7]) + " differences"
                elif self.gui_plot.counter[0] == 'Stratification':
                    filename = self.gui_plot.savefilename
                else:
                    filename = self.value[:-4] + ' ' + zoom
            if len(self.gui_plot.counter) > 1:
                filename = ""
                for n in self.gui_plot.counter:
                    filename = filename + "_" + self.dm.files[n][-6:-4]
                filename = self.dm.mdata[0]["datainici"].strftime("%Y-%m-%d") + "_" \
                           + self.dm.mdata[0]["datafin"].strftime("%Y-%m-%d") + "_Combo of depths" + filename + ' ' + zoom

            file = asksaveasfilename(initialdir='../src/output_images',
                                     filetypes=(("PNG Image", "*.png"), ("JPG Image", "*.jpg"), ("All Files", "*.*")),
                                     defaultextension='.png', initialfile=filename, title="Save as")
            if zoom == 'Zoom':
                self.gui_plot.counter.append(zoom)
            if file:
                self.gui_plot.fig.savefig(file)
                self.dm.mdata[0]['images'].append(
                    file)  # Stores the path of the created images to print them on the report
                self.console_writer('Saving plot in: ', 'action', file, True)
        except (AttributeError, UnboundLocalError, IndexError):
            self.console_writer('Error, couldn\'t find a plot to save', 'warning')

    def merge(self):
        """
        Merges all of the loaded files into a single geojson and txt one
        """
        try:
            self.console_writer('Creating Geojson', 'action')
            df, depths, SN, merging = self.dm.merge()
            if merging is False:
                self.console_writer('Load more than a file for merging, creating an output of only a file instead',
                                    'warning')
            start_time = time.time()
            self.dm.df_to_geojson(df, depths, SN)
            self.dm.df_to_txt(df, SN)
            self.consolescreen.insert("end", "--- %s seconds spend to create a geojson ---" % (
                    time.time() - start_time) + "\n =============\n")
            self.reportlogger.append('Geojson and CSV file created')
        except IndexError:
            self.console_writer('Please, load a file first', 'warning')

    def __historical_merge_window(self):        
        # Creates a new window in order for the user to select the files and 
        # filenames for the historical merger function
        self.newwindow = Toplevel()
        self.newwindow.title('Create Merge Historical')
        # Creates the label, input box and button for the historical file
        Label(self.newwindow, text='Historical:').grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        Button(self.newwindow, text='Browse', command=self.__browse_file).grid(row=0, column=2)
        # Creates the label, input box and button for the new file
        Label(self.newwindow, text='New:').grid(row=1, pady=10)
        self.openfileinput2 = Entry(self.newwindow, width=20)
        self.openfileinput2.grid(row=1, column=1)
        Button(self.newwindow, text='Browse', command=lambda: self.__browse_file(True)).grid(row=1, column=2)
        # Creates the label, input box and button for the output file
        Label(self.newwindow, text='Output file name:').grid(row=2, pady=10)
        self.writefileinput = Entry(self.newwindow, width=20)
        self.writefileinput.grid(row=2, column=1)
        Button(self.newwindow, text='Write',
               command=lambda: self.__call_merger(self.openfileinput.get(), self.openfileinput2.get(),
                                                self.writefileinput.get())).grid(row=2, column=2)

    def __call_merger(self, filename1, filename2, output):
        # Calls the big_merge method under file_writer        
        self.newwindow.destroy()
        self.console_writer('Historical Merge successful!', 'action')
        duplicity = fw.big_merge(filename1, filename2, output)
        if len(duplicity) > 0:
            self.console_writer('Found duplicity between '
                                + str(len(duplicity)) + ' dates. First occurrence at '
                                + str(duplicity[0]) + ' last at ' + str(duplicity[-1]), 'warning')

    def write_excel(self):
        """
        Informs the report and launches the write_excel function
        """
        self.console_writer('Writing the Excel file, please wait this could take some minutes...', 'action')
        input = self.openfileinput.get()
        #output = self.secondInput.get()
        self.newwindow.destroy()
        # fw.Excel(input, '../src/output_files/' + output + '.xlsx')
        ew.excel_writer(input)
        self.console_writer('Excel file successfully created!', 'action')

    def __browse_file(self, merge=False):
        # Browses directories and stores the file selected into a variable
        if merge:
            self.openfileinput2.delete(0, END)
            file = askopenfilename(initialdir='../src/')
            self.openfileinput2.insert(0, file)
        else:
            self.openfileinput.delete(0, END)
            file = askopenfilename(initialdir='../src/')
            self.openfileinput.insert(0, file)

    def __window_browser(self, title, cmd, label1, label2=None):
        # Creates a new pop up window to select different files
        self.newwindow = Toplevel()
        self.newwindow.title(title)

        Label(self.newwindow, text=label1).grid(row=0, pady=10)
        self.openfileinput = Entry(self.newwindow, width=20)
        self.openfileinput.grid(row=0, column=1)
        Button(self.newwindow, text='Browse', command=self.__browse_file).grid(row=0, column=2)

        if label2:
            Label(self.newwindow, text=label2).grid(row=1, pady=10)
            self.secondInput = Entry(self.newwindow, width=20)
            self.secondInput.grid(row=1, column=1)
            Button(self.newwindow, text='Select', command=cmd).grid(row=2, column=1)
        else:
            Button(self.newwindow, text='Select', command=cmd).grid(row=1, column=1)

    def __generate_netCDF(self):
        # Calls the convert_to_netCDF method under DataManager object
        filename = self.openfileinput.get()
        self.newwindow.destroy()
        df = pd.read_csv(filename, sep='\t')
        self.dm.convert_to_netCDF('finalCDM', df, self.consolescreen)

    def __create_heat_spikes(self):
        # Calls the browse_heat_spikes method under HistoricData object
        filename = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        historic = st.HistoricData(filename)
        for i in range(int(year), historic.last_year):
            historic.browse_heat_spikes(i)
        self.console_writer('Plots saved at output_images', 'action')

    def __create_anomalies(self):
        # Calls the browse_anomalies method under HistoricData object
        filename = self.openfileinput.get()
        year = self.secondInput.get()
        self.newwindow.destroy()
        historic = st.HistoricData(filename)
        for i in range(int(year), historic.last_year):
            historic.browse_anomalies(i)
        self.console_writer('Plots saved at output_images', 'action')

    def __create_tridepth_anomalies(self):
        # Calls the multidepht_anomaly_plotter method under HistoricData object
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
        Shows an 'About' message
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

    def close(self):
        """
        Quits and closes the GUI
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            sys.exit()
