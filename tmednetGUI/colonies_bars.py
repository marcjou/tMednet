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
#Palazzu
#df = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/PalazzuPlot.xlsx', index_col=4, header=1, sheet_name='Gràfic Barres')
#df_heat = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/PalazzuPlot.xlsx', index_col=0, header=0, sheet_name='HeatMap')
#PassePalazzu
#df = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/PassePalazzuPlot.xlsx', index_col=0, header=0, sheet_name='Gràfic Barres')
#df_heat = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/PassePalazzuPlot.xlsx', index_col=0, header=0, sheet_name='HeatMap')
#GrotteJo
df = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/GrotteJoPlot.xlsx', index_col=0, header=1, sheet_name='Gràfic Barres')
df_heat = pd.read_excel('/home/marc/Projects/Mednet/tMednet/src/GrotteJoPlot.xlsx', index_col=0, header=0, sheet_name='HeatMap')
# df = pd.read_excel('/home/marcjou/Documentos/CSIC/PalazzuPlot.xlsx', index_col=4, header=1, sheet_name='Gràfic Barres')
#Palazzu
#df = df.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3'])
# PassePalazzu
#df = df.drop(columns=['Unnamed: 1'])
#GrotteJo no hay nada que eliminar
df_markers = df.mask(df == str)
columns = df.columns
df_single = df.copy()
df_single = df_single.drop(columns=columns)
df_marked = df_single.copy()
df_markers = df_markers.fillna('na')
df_partial = df_single.copy()
df_single['End Year'] = 1
df_partial['Necrosis'] = 1
df_partial['Others'] = 1
df_marked['N'] = 1
df_marked['N'] = df_marked['N'].astype('object')
df_marked['O'] = 1
df_marked['O'] = df_marked['O'].astype('object')
df_marked['B'] = 1
df_marked['B'] = df_marked['B'].astype('object')
df_marked['X'] = 1
df_marked['X'] = df_marked['X'].astype('object')
df_zero = df.fillna('na')

def create_dfs(df_single, df_partial):
    for ind in df_single.index:
        u = df_zero.loc[df_zero.index == ind].squeeze()
        df_single['End Year'].loc[df_single.index == ind] = [int(u.index[u.str.contains('M')].values)
                                                             if len(u.index[u.str.contains('M')]) > 0 else 3000]
        print(ind)
    for ind in df_partial.index:
        u = df_zero.loc[df_zero.index == ind].squeeze()
        if len(u.index[u.str.contains('N')]) > 0:
            df_partial['Necrosis'].loc[df_partial.index == ind] = int(u.index[u.str.contains('N')].values[0])
        else:
            df_partial['Necrosis'].loc[df_partial.index == ind] = 3000
        print(ind)
    df_single = df_single.sort_values(by='End Year', ascending=False)
    df_partial = df_partial.sort_values(by='Necrosis', ascending=False)

    return df_single, df_partial

def set_axes(ax, type):
    if type == 'horizontal':
        # Palazzu
        #ax.set_xlim([2003, 2024])
        #ax.set_xticks(range(2003, 2024, 1))
        # PassePalazzu
        #ax.set_xlim([2006, 2024])
        #ax.set_xticks(range(2006, 2024, 1))
        # GrotteJo
        ax.set_xlim([2014, 2024])
        ax.set_xticks(range(2014, 2024, 1))
        ax.tick_params(axis='x', labelrotation=45)
        xticks = ax.xaxis.get_major_ticks()
        xticks[-2].label1.set_visible(False)
        xticks[-3].label1.set_visible(False)
        #xticks[-4].label1.set_visible(False)
        #xticks[-5].label1.set_visible(False)
        # ax.get_yaxis().set_visible(False)
        yticks_positions = [0, len(df_single.index) // 4, len(df_single.index) // 2, (len(df_single.index) // 4) * 3,
                            len(df_single.index) - 1]
        ax.set_yticks(yticks_positions)
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.set_ylabel('% of Alive colonies')
        ax.set_title('Yearly affectation')
    else:
        # Palazzu
        #ax.set_ylim([2003, 2024])
        #ax.set_yticks(range(2003, 2024, 1))
        # PassePalazzu
        #ax.set_ylim([2006, 2024])
        #ax.set_yticks(range(2006, 2024, 1))
        # GrotteJo
        ax.set_ylim([2014, 2024])
        ax.set_yticks(range(2014, 2024, 1))
        yticks = ax.yaxis.get_major_ticks()
        yticks[-2].label1.set_visible(False)
        yticks[-3].label1.set_visible(False)
        #yticks[-4].label1.set_visible(False)
        #yticks[-5].label1.set_visible(False)
        ax.invert_yaxis()
        # ax.get_xaxis().set_visible(False)
        xticks_positions = [0, len(df_single.index) // 4, len(df_single.index) // 2, (len(df_single.index) // 4) * 3,
                            len(df_single.index) - 1]
        ax.set_xticks(xticks_positions)
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.tick_params(axis='x', labelrotation=45)
        ax.set_xlim([-1, len(df_single.index)])
        ax.set_xlabel('% of Alive colonies')
        ax.set_title('Yearly affectation')
def plot_hbars(df_single, df_partial):
    #df_single, df_partial = create_dfs(df_single, df_partial)

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
    # Horizontal bars
    #ax = df_single.plot.barh(figsize=(10, 30), color='#adb5bd', legend=False)
    # Vertical bars
    fig, ax = plt.subplots(figsize=(30, 10))
    #ax = df_single.plot.bar(figsize=(30, 10), color='none', edgecolor='#adb5bd', legend=False, width=0.1)
    ax.vlines(x=df_single.index, ymin=df_single.min(), ymax=df_single['End Year'], linewidth=1)

    set_axes(ax, 'vertical')


    return ax, df_single, df_partial


def plot_markers(ax, df_marked, df_single):
    # Checks marker by marker and plots them in their given position on the bars
    # Eliminated T2_BOTTOM2B and T2-BOTTOM16
    n = 0
    df_marked = df_marked.reindex(df_single.index)
    df_marked = df_marked.drop('SetUp')
    for ind in df_marked.index:
        u = df_marked.loc[df_marked.index == ind].squeeze()
        if len(u['N']) > 0:
            for i in range(0, len(u['N'])):
                # ax.scatter(ind, u['N'][i], marker='o', c='red', s=10, label='N')
                #ax.plot(u['N'][i], n, marker='<', color='#00a6fb', markersize=7, label='N')
                ax.plot( n, int(u['N'][i]), marker='<', color='#00a6fb', markersize=7, label='N')
        if len(u['O']) > 0:
            for i in range(0, len(u['O'])):
                #ax.plot(u['O'][i], n, marker='o', color='#0582ca', markersize=7, label='O')
                ax.plot(n, int(u['O'][i]), marker='o', color='#0582ca', markersize=7, label='O')
        if len(u['B']) > 0:
            for i in range(0, len(u['B'])):
                #ax.plot(u['B'][i], n, marker='d', color='#006494', markersize=7, label='B')
                ax.plot(n, int(u['B'][i]), marker='d', color='#006494', markersize=7, label='B')
        if len(u['X']) > 0:
            for i in range(0, len(u['X'])):
                #ax.plot(u['X'][i], n, marker='P', color='#003554', markersize=10, label='X')
                ax.plot(n, int(u['X'][i]), marker='P', color='#003554', markersize=10, label='X')
        n += 1
    # Create custom legend handles (one for each marker type)
    legend_elements = [
        Line2D([0], [0], marker='<', color='#00a6fb', label='Necrosis', markerfacecolor='#00a6fb', markersize=10),
        Line2D([0], [0], marker='o', color='#0582ca', label='Overgrowth', markerfacecolor='#0582ca', markersize=10),
        Line2D([0], [0], marker='d', color='#006494', label='Breakage', markerfacecolor='#006494', markersize=10),
        Line2D([0], [0], marker='P', color='#003554', label='Others', markerfacecolor='#003554', markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='lower right')


def savefigure(title):
    plt.savefig('/home/marc/Projects/Mednet/tMednet/src/'+ title + '.png')

def plot_curve_death(df_single):
    plt.clf()
    # PassePalazzu
    #df_single.loc['SetUp'] = 2006
    # GrotteJo
    df_single.loc['SetUp'] = 2014
    df_single = df_single.sort_values(by='End Year', ascending=False)
    plt.plot(df_single['End Year'].values, df_single.index)
    # Palazzu
    #plt.xlim([2003, 2023.05])
    #plt.xticks(range(2003, 2024, 1))
    # PassePalazzu
    #plt.xlim([2006, 2023.05])
    #plt.xticks(range(2006, 2024, 1))
    # GrotteJo
    plt.xlim([2014, 2023.05])
    plt.xticks(range(2014, 2024, 1))
    plt.tick_params(axis='x', labelrotation=45)
    xticks = plt.gca().xaxis.get_major_ticks()
    xticks[-2].label1.set_visible(False)
    xticks[-3].label1.set_visible(False)
    #xticks[-4].label1.set_visible(False)
    #xticks[-5].label1.set_visible(False)
    # ax.get_yaxis().set_visible(False)
    yticks_positions = [0, len(df_single.index) // 4, len(df_single.index) // 2, (len(df_single.index) // 4) * 3,
                        len(df_single.index) - 1]
    plt.yticks(yticks_positions, ['0%', '25%', '50%', '75%', '100%'])
    plt.ylabel('% of Alive colonies')
    plt.title('Survival')

def plot_partial_curve_death(df_partial):
    plt.clf()
    plt.plot(df_partial['Necrosis'].values, df_partial.index)
    # Palazzu
    #plt.xlim([2003, 2023.05])
    #plt.xticks(range(2003, 2024, 1))
    # PassePalazzu
    #plt.xlim([2006, 2023.05])
    #plt.xticks(range(2006, 2024, 1))
    # GrotteJo
    plt.xlim([2014, 2023.05])
    plt.xticks(range(2014, 2024, 1))
    plt.tick_params(axis='x', labelrotation=45)
    xticks = plt.gca().xaxis.get_major_ticks()
    xticks[-2].label1.set_visible(False)
    xticks[-3].label1.set_visible(False)
    #xticks[-4].label1.set_visible(False)
    #xticks[-5].label1.set_visible(False)
    # ax.get_yaxis().set_visible(False)
    yticks_positions = [0, len(df_single.index) // 4, len(df_single.index) // 2, (len(df_single.index) // 4) * 3,
                        len(df_single.index) - 1]
    plt.yticks(yticks_positions, ['0%', '25%', '50%', '75%', '100%'])
    plt.ylabel('% of Alive colonies')
    plt.title('Affected by partial mortality')

#ax, df_single, df_partial = plot_hbars(df_single, df_partial)
#plot_markers(ax, df_marked, df_single)
#savefigure('palazzu_bars')
df_single, df_partial = create_dfs(df_single, df_partial)
plot_curve_death(df_single)
savefigure('grottejo_curve')

plot_partial_curve_death(df_partial)
savefigure('grottejo_curve_partial')

ax, df_single, df_partial = plot_hbars(df_single, df_partial)
plot_markers(ax, df_marked, df_single)
savefigure('grottejo_bars')

'''
df_heat = df_heat.fillna(100)
df_heat = df_heat.reindex(df_single.sort_values(by='End Year').index)
fig2, ax2 = plt.subplots(figsize=(20, 20))
cmap = matplotlib.cm.get_cmap('YlOrBr', 256)
new_cmap = matplotlib.cm.colors.ListedColormap(cmap(np.linspace(0.1, 0.9, 256)))
sns.heatmap(df_heat, ax=ax2, cmap=new_cmap, linewidths=1, linecolor='black')
ax2.get_yaxis().set_visible(False)
fig2.savefig("/home/marc/Projects/Mednet/tMednet/src/palazzu_heatmap YlOrBr.png")
'''
print('hi')
