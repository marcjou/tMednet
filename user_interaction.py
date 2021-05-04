import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename, asksaveasfilename, askdirectory
from tkinter import messagebox, Button
from tkinter import scrolledtext
from PIL import Image, ImageTk

import file_manipulation as fm
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

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
        editmenu.add_command(label="Plot1", command=self.help)
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

        self.list = tk.Listbox(frame1)
        self.list.grid(row=0, column=0, sticky="ewns")
        self.list.bind("<<ListboxSelect>>", self.selectlist)

        cscrollb = tk.Scrollbar(frame2, width=20)
        cscrollb.grid(row=0, column=1, sticky="ns")
        self.textBox = tk.Text(frame2, bg="black", fg="white", height=10, yscrollcommand=cscrollb.set)
        self.textBox.grid(row=0, column=0, sticky="nswe")
        cscrollb.config(command=self.textBox.yview)

        self.consolescreen = tk.Text(f1, bg='black', height=1, fg='white')
        self.consolescreen.grid(row=1, column=0, sticky='nsew')
        self.consolescreen.bind("<Key>", lambda e: "break") # Makes the console uneditable


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

        w = evt.widget  # Que es EVT???
        index = int(w.curselection()[0])
        if index in self.index:
            pass
        else:
            self.value = w.get(index)
            print(index, self.value)
            self.consolescreen.insert("end", "Plotting: " + self.value + "\n =============\n")

            self.index.append(index)
            self.counter.append(index)  # Keeps track of how many plots there are and the index of the plotted files
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
        filesname, self.path = fm.openfile(self, files, self.consolescreen)

        for file in filesname:  # Itera toda la lista de archivos para añadirlos a la listbox
            self.files.append(file)
        fm.loaddata(self, self.consolescreen)  # Llegim els fitxers

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
        try:
            fm.to_utc(self)
        except IndexError:
            messagebox.showerror('Error', 'Load a file before converting to UTC')

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
        self.consolescreen.insert("end", "Clearing Plots \n =============\n")
        self.index = []
        self.counter = []
        self.plot.clear()
        self.canvas.draw()

    def onSave(self):
        """
        Method: onSave(self)
        Purpose: Saves the file with a proposed name and lets the user choose one of their liking.
        Require:
        Version:
        01/2021, EGL: Documentation
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

            file = asksaveasfilename(filetypes=(("PNG Image", "*.png"), ("JPG Image", "*.jpg"), ("All Files", "*.*")),
                                     defaultextension='.png', initialfile=filename, title="Save as")
            if file:
                self.fig.savefig(file)
        except (AttributeError, UnboundLocalError, IndexError):
            messagebox.showerror("Error", "Plot a file first")
            self.consolescreen.insert("end", "Error, couldn't find a plot to save\n =============\n")

    def help(self):
        """
        Version:
        01/2021, EGL: Documentation
        """

        top = Toplevel()
        top.title("About...")

        img = Image.open("./TMEDNET_White.png").resize((250, 78))
        photo = ImageTk.PhotoImage(img)
        label = Label(top, image=photo)
        label.image = photo  # keep a reference!
        text = Label(top, text='Version: ' + version + '\nAuthor: Marc Jou \nBuild: ' + build)
        label.pack()
        text.pack()
        # messagebox.showinfo('About', 'Version: ' + version + '\nAuthor: Marc Jou \nBuild: ' + build)
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
