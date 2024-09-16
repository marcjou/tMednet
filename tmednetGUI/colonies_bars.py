import sys
import time
import matplotlib
import seaborn as sns

matplotlib.use('Agg')
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
from matplotlib.lines import Line2D
import matplotlib.dates as dates
from mpl_toolkits.axisartist.axislines import Subplot
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from tkinter import messagebox, Button
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

df = pd.read_excel('/home/marcjou/Escritorio/Projects/tMednet/src/PalazzuPlot.xlsx', index_col=4, header=1, sheet_name='Gràfic Barres')
df_heat = pd.read_excel('/home/marcjou/Escritorio/Projects/tMednet/src/PalazzuPlot.xlsx', index_col=0, header=0, sheet_name='HeatMap')
# df = pd.read_excel('/home/marcjou/Documentos/CSIC/PalazzuPlot.xlsx', index_col=4, header=1, sheet_name='Gràfic Barres')
df = df.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3'])
df_markers = df.mask(df == str)
columns = df.columns
df_single = df.copy()
df_single = df_single.drop(columns=columns)
df_marked = df_single.copy()
df_markers = df_markers.fillna('na')
df_single['End Year'] = 1
df_marked['N'] = 1
df_marked['N'] = df_marked['N'].astype('object')
df_marked['O'] = 1
df_marked['O'] = df_marked['O'].astype('object')
df_marked['B'] = 1
df_marked['B'] = df_marked['B'].astype('object')
df_marked['X'] = 1
df_marked['X'] = df_marked['X'].astype('object')
df_zero = df.fillna('na')


def plot_hbars(df_single):
    for ind in df_single.index:
        u = df_zero.loc[df_zero.index == ind].squeeze()
        df_single['End Year'].loc[df_single.index == ind] = [int(u.index[u.str.contains('M')].values)
                                                             if len(u.index[u.str.contains('M')]) > 0 else columns[-1]]
        print(ind)

    for ind in df_marked.index:
        u = df_markers.loc[df_markers.index == ind].squeeze()
        df_marked.at[ind, 'N'] = list(u.index[u.str.contains('N')].values) if len(
            u.index[u.str.contains('N')]) > 0 else []
        df_marked.at[ind, 'O'] = list(u.index[u.str.contains('O')].values) if len(
            u.index[u.str.contains('O')]) > 0 else []
        df_marked.at[ind, 'B'] = list(u.index[u.str.contains('B')].values) if len(
            u.index[u.str.contains('B')]) > 0 else []
        df_marked.at[ind, 'X'] = list(u.index[u.str.contains('X')].values) if len(
            u.index[u.str.contains('X')]) > 0 else []
        print(ind)
    df_single = df_single.sort_values(by='End Year', ascending=False)
    ax = df_single.plot.barh(figsize=(10, 30), color='#adb5bd', legend=False)
    ax.set_xlim([2003, 2025])
    ax.set_xticks(range(2003, 2026, 1))
    ax.tick_params(axis='x', labelrotation=45)
    xticks = ax.xaxis.get_major_ticks()
    xticks[-4].label1.set_visible(False)
    xticks[-5].label1.set_visible(False)
    xticks[-7].label1.set_visible(False)
    ax.get_yaxis().set_visible(False)
    return ax, df_single


def plot_markers(ax, df_marked, df_single):
    # Checks marker by marker and plots them in their given position on the bars
    # Eliminated T2_BOTTOM2B and T2-BOTTOM16
    n = 0
    df_marked = df_marked.reindex(df_single.index)
    for ind in df_marked.index:
        u = df_marked.loc[df_marked.index == ind].squeeze()
        if len(u['N']) > 0:
            for i in range(0, len(u['N'])):
                # ax.scatter(ind, u['N'][i], marker='o', c='red', s=10, label='N')
                ax.plot(u['N'][i], n, marker='<', color='#00a6fb', markersize=7, label='N')
        if len(u['O']) > 0:
            for i in range(0, len(u['O'])):
                ax.plot(u['O'][i], n, marker='o', color='#0582ca', markersize=7, label='O')
        if len(u['B']) > 0:
            for i in range(0, len(u['B'])):
                ax.plot(u['B'][i], n, marker='d', color='#006494', markersize=7, label='B')
        if len(u['X']) > 0:
            for i in range(0, len(u['X'])):
                ax.plot(u['X'][i], n, marker='P', color='#003554', markersize=10, label='X')
        n += 1
    # Create custom legend handles (one for each marker type)
    legend_elements = [
        Line2D([0], [0], marker='<', color='#00a6fb', label='Necrosis', markerfacecolor='#00a6fb', markersize=10),
        Line2D([0], [0], marker='o', color='#0582ca', label='Overgrowth', markerfacecolor='#0582ca', markersize=10),
        Line2D([0], [0], marker='d', color='#006494', label='Breakage', markerfacecolor='#006494', markersize=10),
        Line2D([0], [0], marker='P', color='#003554', label='Others', markerfacecolor='#003554', markersize=10),
    ]
    ax.legend(handles=legend_elements)


def savefigure():
    plt.savefig('/home/marcjou/palazzu_bars.png')



ax, df_single = plot_hbars(df_single)
plot_markers(ax, df_marked, df_single)
savefigure()


df_heat = df_heat.fillna(100)
df_heat = df_heat.reindex(df_single.sort_values(by='End Year').index)
fig2, ax2 = plt.subplots(figsize=(20, 20))
sns.heatmap(df_heat, ax=ax2, cmap='RdYlGn_r', linewidths=1, linecolor='black')
ax2.get_yaxis().set_visible(False)
fig2.savefig("/home/marcjou/heatmap_blankis red.png")

print('hi')
