import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import mortality_frequency as mf
import cartopy.crs as ccrs
from hexalattice.hexalattice import *



achi = mf.MME_Plot('../src/MME.xlsx')
achi.plot_yearly_fish_assesment()
#achi.plot_affected_number()
#achi.regional_map_composer()
#achi.plot_data_map()

# Proba de nou grafic de Quim el MegaGraph
total_numbers = achi.df_events # Number of total hexagons affected per year dataset
total_records = achi.df_numbers # Number of total records per year dataset

df_third = achi.get_numbered_df()
df_third['Year'] = df_third['Year'].astype(int)

#TODO Incluir en get numbered df
df_records = pd.DataFrame(achi.columns, columns=['Year'])
df_records['Count'] = 0
for year in achi.columns:
    df_records['Count'].loc[df_records['Year'] == year] = total_records[int(year)].sum()

# df that contains number of ecoregions affected by year
df_affected_regions = pd.DataFrame(achi.columns, columns=['Year'])
df_affected_regions['Count'] = 0
for year in achi.columns:
    df_affected_regions['Count'].loc[df_affected_regions['Year'] == year] = len(total_numbers['sub-ecoregion'].loc[total_numbers[year] >= 1].unique())
df_records['Cumulative'] = df_records['Count'].cumsum()

trecords = df_records['Cumulative'].iloc[-1]
df_records['PercentageCum'] = (df_records['Cumulative'] / trecords) * 100


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)

par1 = host.twinx()
par2 = host.twinx()

# Offset the right spine of par2.  The ticks and label have already been
# placed on the right by twinx above.
par2.spines["right"].set_position(("axes", 1.2))
# Having been created by twinx, par2 has its frame off, so the line of its
# detached spine is invisible.  First, activate the frame but make the patch
# and spines invisible.
make_patch_spines_invisible(par2)
# Second, show the right spine.
par2.spines["right"].set_visible(True)

w = 0.3

p1 = host.bar(df_third['Year'].astype(int)-w, df_third['Count'], width=w, color='tab:blue', align='center', label='Hexagons')
p2 = par1.bar(df_records['Year'].astype(int), df_records['Count'], width=w, color='tab:orange', align='center', label='Records')
p3, = par2.plot(df_records['Year'].astype(int), df_records['PercentageCum'], color='black', label='Cumulative', marker='.')
'''
host.set_xlim(0, 2)
host.set_ylim(0, 2)
par1.set_ylim(0, 4)
par2.set_ylim(1, 65)
'''
host.set_xlabel("Year")
host.set_ylabel("# of affected hexagons")
par1.set_ylabel("# of records")
par2.set_ylabel("Cumulative % of MME records")

host.yaxis.label.set_color('tab:blue')
par1.yaxis.label.set_color('tab:orange')
par2.yaxis.label.set_color('black')

tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors='tab:blue', **tkw)
par1.tick_params(axis='y', colors='tab:orange', **tkw)
par2.tick_params(axis='y', colors='black', **tkw)
host.tick_params(axis='x', **tkw)

myl = [p1] + [p2] + [p3]
host.legend(myl, [l.get_label() for l in myl], loc='upper left')

i = 0
for rect in p2:
    text = df_affected_regions['Count'][i]
    height = rect.get_height()
    #circle = patches.Ellipse((rect.get_x(), height + 4.5), 1, 10, facecolor='None', edgecolor='black')
    #par1.add_patch(circle)
    par1.text(rect.get_x(), height, f'{text:.0f}', ha='center')
    i += 1


ax = plt.subplot(111)
w = 0.3

ax.bar(df_third['Year'].astype(int)-w, df_third['Count'], width=w, color='b', align='center')
bar_props = ax.bar(df_records['Year'].astype(int), df_records['Count'], width=w, color='r', align='center')
i = 0
for rect in bar_props:
    text = df_affected_regions['Count'][i]
    height = rect.get_height()
    plt.text(rect.get_x(), height, f'{text:.0f}', ha='center', va='bottom')
    i += 1

ax2 = ax.twinx()



ax2.plot(df_records['Year'].astype(int), df_records['Cumulative'])

ax2.set_ylabel('Cumulative # of MME records')
ax.set_ylabel('# of affected hexagons and records')


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






