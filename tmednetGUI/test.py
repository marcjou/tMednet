import pandas as pd
from matplotlib.lines import Line2D
import numpy as np
from matplotlib.patches import Patch
from datetime import datetime as dt
import matplotlib.pyplot as plt


df = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202311.txt', '\t')
df['Month'] = pd.to_datetime(df['Date'], dayfirst=True).dt.month
df['Year'] = pd.to_datetime(df['Date'], dayfirst=True).dt.year
legend_elements = [Line2D([0], [0], color='orange', lw=1.5, label='Median'),
                   Line2D([0], [0], color='green', lw=1, label='Mean', linestyle='--')]

for year in [2015, 2016, 2017, 2022]:
    for depth in ['10', '15', '20', '25']:
        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        df.loc[(df['Year'] == year) & (df['Month'] >= 6) & (df['Month'] <= 9)].boxplot(column=depth, by=['Month'], ax=ax, notch=True, grid=False, showmeans = True, meanline = True, patch_artist = True,
               boxprops = dict(facecolor = "lightblue"), medianprops = dict(color = "orange", linewidth = 1.5))
        ax.set_title('Median summer temperature ' + str(depth) + 'm ' + str(year))
        ax.set_xlabel('Month')
        ax.set_ylabel('Temperature (ºC)')
        ax.set_xticklabels(['June', 'July', 'August', 'September'])
        ax.legend(handles=legend_elements)
        ax.set_ylim(14, 28)
        plt.savefig('../src/output_images/Median temp_' + str(year) + '_' + str(depth))

for depth in ['10', '15', '20', '25']:
    fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
    ax = fig.add_subplot(1, 1, 1)
    df.loc[(df['Year'] == 2015) | (df['Year'] == 2016) | (df['Year'] == 2017) | (df['Year'] == 2022) & (df['Month'] >= 6) & (df['Month'] <= 9)].boxplot(column=depth, by=['Year'], ax=ax, notch=True, grid=False, showmeans = True, meanline = True, patch_artist = True,
               boxprops = dict(facecolor = "lightblue"), medianprops = dict(color = "orange", linewidth = 1.5))
    ax.set_title('Median summer temperature ' + str(depth) + 'm')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature (ºC)')
    ax.legend(handles=legend_elements)
    ax.set_ylim(10, 28)
    plt.savefig('../src/output_images/Median temp_' + str(depth))

print('he')