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

df = pd.read_excel('/home/marc/Documentos/CSIC/PalazzuPlot.xlsx', index_col=4, header=1)
df = df.drop(columns=['Unnamed: 0','Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3'])
df_markers = df.mask(df == str)
columns = df.columns
df_single = df.copy()
df_single = df_single.drop(columns=columns)
df_single['End Year'] = 1
df_zero = df.fillna('na')
for ind in df_single.index:
    u = df_zero.loc[df_zero.index == ind].squeeze()
    df_single['End Year'].loc[df_single.index == ind] = [int(u.index[u.str.contains('M')].values)
                                                         if len(u.index[u.str.contains('M')]) > 0 else columns[-1]]
    print(ind)


print('hi')