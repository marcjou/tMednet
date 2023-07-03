import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import mortality_frequency as mf

achi = mf.MME_Plot('../src/MME.xlsx')
achi.regional_map_composer()
achi.plot_data_map()
achi.heatmap_base_composer()

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
                bbox_inches='tight')






