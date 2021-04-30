import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename, asksaveasfilename, askdirectory
from tkinter import messagebox, Button
from tkinter import scrolledtext

import file_manipulation as fm
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


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
        filemenu.add_command(label="Open", command=self.onOpen)
        filemenu.add_command(label="Save", command=self.onSave)
        filemenu.add_command(label="Report", command=self.report)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=lambda: cerrar(self))
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="To UTC", command=self.to_utc)
        editmenu.add_command(label="Plot1", command=self.donothing)
        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.donothing)
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
        self.canvas = FigureCanvasTkAgg(self.fig, master=f2)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, f2)
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

        self.list = tk.Listbox(frame1)
        self.list.grid(row=0, column=0, sticky="ewns")
        self.list.bind("<<ListboxSelect>>", self.selectlist)

        cscrollb = tk.Scrollbar(frame2, width=20)
        cscrollb.grid(row=0, column=1, sticky="ns")
        self.textBox = tk.Text(frame2, bg="black", fg="white", height=10, yscrollcommand=cscrollb.set)
        self.textBox.grid(row=0, column=0, sticky="nswe")
        cscrollb.config(command=self.textBox.yview)

    # p.add(f1,width=300)
    # p.add(f2,width=1200)

    def selectlist(self, evt):
        """
		Method: clear_plots(self)
		Purpose: Clear plot
		Require:
			canvas: refrence to canvas widget
			subplot: plot object
		Version: 01/2021, EGL: Documentation
		"""

        w = evt.widget # Que es EVT???
        index = int(w.curselection()[0])
        if index in self.index:
            pass
        else:
            self.value = w.get(index)
            print(index, self.value)
            self.index.append(index)
            # dibuixem un cop seleccionat
            self.plot_ts(index)

        # fm.loaddata(self)  Que fa això aquí???? Investigar [[DEPRECATED??]]

    def onOpen(self):
        """
        Method: onOpen(self)
        Purpose: Launches the askopen widget to set data filenames
        Require:
        Version: 01/2021, EGL: Documentation
        """

        self.path = "./"
        files = askopenfilenames(initialdir=self.path, title="Open files",
                                 filetypes=[("All files", "*.*")])
        filesname, self.path = fm.openfile(self, files, END)

        for file in filesname:  # Itera toda la lista de archivos para añadirlos a la listbox
            self.files.append(file)
        fm.loaddata(self)  # Llegim els fitxers

        return

    def report(self):
        """
		Method: report(self)
		Purpose: List main file characteristics
		Require:
			textBox: text object
		Version: 01/2021, EGL: Documentation
		"""

        fm.report(self, self.textBox, END)

    def to_utc(self):
        """
        Method: to_utc(self)
        Purpose: Shift temporal axis
        Require:
        Version: 01/2021, EGL: Documentation
        """

        fm.to_utc(self)

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

        self.plot.plot(self.mdata[index]['timegmt'], self.mdata[index]['temp'],
                       '-', label=str(self.mdata[index]['depth']))
        self.plot.set(ylabel='Temperature (DEG C)',
                      title=self.files[index] + "\n" + 'Depth:' + str(self.mdata[index]['depth']) + " - Region: " + str(
                          self.mdata[index]['region']))
        self.plot.legend()
        # fig.set_size_inches(14.5, 10.5, forward=True)
        self.canvas.draw()

    def plot_dif(self):
        """
        Method: plot_dif(self)
        Purpose: Plot time series of differences
        Require:
            canvas: refrence to canvas widget
            subplot: axis object
        Version:
        01/2021, EGL: Documentation
        """
        pass

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
        self.index = []
        self.plot.clear()
        self.canvas.draw()

    def onSave(self):
        """
        Method: onSave(self)
        Purpose:
        Require:
        Version:
        01/2021, EGL: Documentation
        """
        self.fig.savefig(self.value[:-4]+".png")

    def donothing(self):
        """
        Version:
        01/2021, EGL: Documentation
        """
        pass


def cerrar(root):
    """
    Function: cerrar():
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


def main():
    root = Tk()
    # root.minsize(1000,500)
    root.title("TMEDNET tool")

    app = tmednet(root)
    root.protocol("WM_DELETE_WINDOW", lambda: cerrar(root))
    root.mainloop()


if __name__ == '__main__':
    main()
