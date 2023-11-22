import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import mortality_frequency as mf
import cartopy.crs as ccrs
from hexalattice.hexalattice import *
import surface_temperature as st





achi = mf.MME_Plot('../src/MME.xlsx')
ochi = mf.MME_Plot('../src/MME.xlsx')

achi.affected_by_ecoregion()

#achi.create_full_census_plots()
#achi.plot_fish_assesment_zoom()
#achi.plot_yearly_fish_assesment_zoom()
#achi.mortality_assesment_census()

# Species Esingularis Pclavata
#achi.plot_mortality_assesment_zoom(specie='Pclavata')
#achi.recent_old_mortality()
#achi.palamos_capdecreus()
#achi.mortality_by_species()
#achi.plot_yearly_mortality_assesment_zoom()

#achi.plot_yearly_mortality_assesment_zoom()

#achi.horizontal_mortality_percentage(type='depth')


#achi.plot_affected_number()
#achi.regional_map_composer()
#achi.plot_data_map()

# Proba de nou grafic de Quim el MegaGraph

total_numbers = achi.df_events # Number of total hexagons affected per year dataset
total_records = achi.df_numbers # Number of total records per year dataset

df_third = achi.get_numbered_df()
df_third['Year'] = df_third['Year'].astype(int)
df_third['Cumulative'] = df_third['Count'].cumsum()
thex = df_third['Cumulative'].iloc[-1]

df_third['PercentageCum'] = (df_third['Cumulative'] / thex) * 100


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

#par1 = host.twinx()
par2 = host.twinx()

# Offset the right spine of par2.  The ticks and label have already been
# placed on the right by twinx above.
#par2.spines["right"].set_position(("axes", 1.2))
# Having been created by twinx, par2 has its frame off, so the line of its
# detached spine is invisible.  First, activate the frame but make the patch
# and spines invisible.
#make_patch_spines_invisible(par2)
# Second, show the right spine.
par2.spines["right"].set_visible(True)

w = 0.5

p1 = host.bar(df_third['Year'].astype(int), df_third['Count'], width=w, color='tab:blue', align='center', label='Hexagons')
#p2 = par1.bar(df_records['Year'].astype(int), df_records['Count'], width=w, color='tab:orange', align='center', label='Records')
p3, = par2.plot(df_records['Year'].astype(int), df_third['PercentageCum'], color='black', label='Cumulative', marker='.')

host.set_xlabel("Year")
host.set_ylabel("# of affected hexagons")
#par1.set_ylabel("# of records")
par2.set_ylabel("Cumulative % of affected hexagons")

host.yaxis.label.set_color('tab:blue')
#par1.yaxis.label.set_color('tab:orange')
par2.yaxis.label.set_color('black')

tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors='tab:blue', **tkw)
#par1.tick_params(axis='y', colors='tab:orange', **tkw)
par2.tick_params(axis='y', colors='black', **tkw)
host.tick_params(axis='x', **tkw)
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
host.set_xlim([1978.5, 2020.5])
host.xaxis.set_major_locator(MultipleLocator(5))
host.xaxis.set_minor_locator(MultipleLocator(1))

#myl = [p1] + [p2] + [p3]
myl = [p1] + [p3]
#myl = [p1]
host.legend(myl, [l.get_label() for l in myl], loc='upper left')


'''
i = 0
for rect in p2:
    text = df_affected_regions['Count'][i]
    height = rect.get_height()
    #circle = patches.Ellipse((rect.get_x(), height + 4.5), 1, 10, facecolor='None', edgecolor='black')
    #par1.add_patch(circle)
    par1.text(rect.get_x(), height, f'{text:.0f}', ha='center')
    i += 1
'''

plt.savefig('Cachiplot.png',bbox_inches='tight')



