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

    def __init__(self, f2):
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
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def __str__(self):
        return "GUIPlot object of {}".format(self.site_name)

    def get_args(self):
        return self.fig, self.plot, self.plot1, self.plot2, self.cbexists, self.canvas
