import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import mortality_frequency as mf
import cartopy.crs as ccrs
from hexalattice.hexalattice import *



achi = mf.MME_Plot('../src/MME.xlsx')
#achi.regional_map_composer()
#achi.plot_data_map()

#TODO set the ranges of assesment
urgh = pd.read_excel('../src/Mortality Atención Corales.xlsx', 'Mortality Data')
ax, gl = achi.ax_setter()
urgh['Assesment'] = urgh['% Affected all'].apply(
            lambda y: 0 if y <= 10 else (1 if y <= 30 else (2 if y < 60 else 3)))
colors = ['green', 'yellow', 'orange', 'red']
cmap = LinearSegmentedColormap.from_list('Custom', colors, len(colors))
asses = ax.scatter(x=urgh['LONG'], y=urgh['LAT'], c=urgh['Assesment'],
                            transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0, vmax=3, zorder=10)
cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])

'''
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

hex = mpatches.RegularPolygon(xy=[-70,-45], numVertices=6, radius=15, edgecolor='k', facecolor='red', transform=ccrs.PlateCarree())
ax.add_patch(hex)
#Create hexagonal grid
r_lat = 25/110.574 # Radius of hexagon in lat degree
r_lon = 25/111.320*np.cos(np.radians(r_lat))
ratio2 = 46.5 / 22 #Ratio of rectangle
N = 800 # Number of hexagons I want in my grid
ratio = np.sqrt(3)/2 # cos(60°)
N_X = int(np.sqrt(N)/ratio)
N_Y = N // N_X
N_X = 46.5 // r_lon
N_Y = N_X // ratio2
xv, yv = np.meshgrid(np.arange(N_X), np.arange(N_Y), sparse=False, indexing='xy')
xv = xv * ratio
xv[::2, :] += ratio/2
xv = xv*r_lon*2 -9.5
yv = yv*r_lat*2 + 28

for i in range(0, len(xv[0])):
    for j in range(0, len(xv[:,0])):
        hex = mpatches.RegularPolygon(xy=[xv[j, i], yv[j, i]], numVertices=6, radius=r_lon, alpha=0.3, edgecolor='k',
                                      transform=ccrs.PlateCarree())
        ax.add_patch(hex)
'''

plt.clf()
urgh = pd.read_excel('../src/Example_Visual_census_ALL.xlsx', 'DATA-All')
ax, gl = achi.ax_setter()
urgh['Assesment'] = urgh['Tropical. Index'].apply(
            lambda y: 0 if y <= 1 else (1 if y <= 3 else (2 if y <= 5 else 3)))
colors = ['green', 'yellow', 'orange', 'red']
cmap = LinearSegmentedColormap.from_list('Custom', colors, len(colors))
asses = ax.scatter(x=urgh['LONG'], y=urgh['LAT'], c=urgh['Assesment'],
                            transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0, vmax=3, zorder=10)
cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
# Coral assessment No impact, Low Impact, Moderate Impact, High Impact
plt.savefig('../src/output_images/Fish Assesment.png',
            bbox_inches='tight')

for year in urgh['YEAR'].unique():
    plt.clf()
    ax, gl = achi.ax_setter()
    df = urgh.loc[urgh['YEAR'] == year]
    asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment'],
                       transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0, vmax=3, zorder=10)
    cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
    cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
    plt.title('Fish census ' + str(year))
    plt.savefig('../src/output_images/Fish Assesment_' + str(year) + '.png',
                bbox_inches='tight')

'''
ex = pd.read_excel('../src/MME.xlsx', sheet_name='Quim Years with MME')

ex.columns = ex.columns.astype(str)
columns = ex.columns[4:]

ex_copy = ex.copy()
ex_copy.replace(0, np.nan, inplace=True)
ex_copy.index = ex_copy['sub-ecoregion']
for i in ex.columns[:4]:
    del ex_copy[i]
myColors = ((1.0, 1.0, 1.0, 1.0), (0.8, 0.0, 0.0, 1.0))
cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
# Get the first index of every ecoregion for yticks
reg = ex_copy.index.unique()
yticks = []
for i in reg:
    yticks.append(ex_copy.index.get_indexer_for((ex_copy[ex_copy.index == i].index))[0])
num_ticks = len(reg)
reg_list = ex_copy.index
# the content of labels of these yticks
yticklabels = [reg_list[idx] for idx in yticks]

ax = sns.heatmap(ex_copy, cmap=cmap, yticklabels=yticklabels, vmax=1, vmin=0, cbar_kws={'ticks' : [0,1]}, linewidth=0.05, linecolor='black')
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)

for n in ex_copy.index.unique():
    plt.clf()
    ax = sns.heatmap(ex_copy.loc[ex_copy.index == n], cmap=cmap, yticklabels=False, vmax=1, vmin=0, cbar_kws={'ticks' : [0,1]})
    ax.set_ylabel(n)
    plt.savefig('../src/output_images/Heatmap MME_' + n + '.png',
                bbox_inches='tight')


ex_numbers = pd.read_excel('../src/MME.xlsx', sheet_name='Massimo original dataset')
ex_numbers.columns = ex_numbers.columns.astype(str)
ex_numbers_copy = ex_numbers.copy()
ex_numbers_copy.index = ex_numbers_copy['sub-ecoregion']
for i in ex_numbers.columns[:3]:
    del ex_numbers_copy[i]
ex_numbers_copy.replace(0, np.nan, inplace=True)
myColors2 = [(1.0, .7, .7, 1.0)]
x = float(0.7/ex_numbers_copy.max().max())
xy = 0.2/ex_numbers_copy.max().max()
old_col = .7
old_col_one = 1.0
for i in range(1, int(ex_numbers_copy.max().max()) + 1):
    myColors2.append((old_col_one - xy*i, old_col - x, old_col - x, 1.0))
    old_col = old_col - x
myColors2 = tuple(myColors2)
cmap2 = LinearSegmentedColormap.from_list('Custom', myColors2, len(myColors2))

ax = sns.heatmap(ex_numbers_copy, cmap=cmap2, yticklabels=yticklabels)
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)

for n in ex_copy.index.unique():
    plt.clf()
    ax = sns.heatmap(ex_numbers_copy.loc[ex_numbers_copy.index == n], cmap=cmap2, yticklabels=False)
    ax.set_ylabel(n)
    plt.savefig('../src/output_images/Heatmap MME_N_' + n + '.png',
                bbox_inches='tight')'''






