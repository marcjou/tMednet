import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
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

df_return = ex.copy()
ret_counter = 0
old_year = ''
for idx, row in ex.iterrows():
    for year in columns:
        if row[year] == 1 or year == columns[-1]:
            if year == '2020':
                print('ye')
            ret_counter = ret_counter + 1
            if old_year == '':
                old_year = year
                if year == columns[-1]:
                    old_year = ''
                    ret_counter = 0
                    df_return[year][idx] = np.nan
            else:
                if year == columns[-1]:
                    df_return[old_year][idx] = np.nan
                    df_return[year][idx] = np.nan
                    old_year = ''
                    ret_counter = 0
                else:
                    if ret_counter - 1 <= 0:
                        df_return[old_year][idx] = np.nan
                    else:
                        df_return[old_year][idx] = ret_counter - 1
                    ret_counter = 1
                    old_year = year
        else:
            df_return[year][idx] = np.nan
            if ret_counter != 0:
                ret_counter = ret_counter + 1

df_scatter = df_return.melt(id_vars=['sub-ecoregion', 'id.hexagon', '#Years with MME',
       '#Records MMEs_All_years_'], var_name='Year', value_name='Return time')

df_scatter['Year'] = df_scatter['Year'].astype(int)

dict_for_yearly = {'Year' : '', 'Return years' : 0, 'Count' : 0}


dict_list_yearly = []
for i in range(1, 41):
    for year in df_scatter['Year'].unique():
        dict_for_yearly['Year'] = year
        dict_for_yearly['Return years'] = i
        dict_for_yearly['Count'] = df_scatter['Return time'].loc[(df_scatter['Year'] == year) & (df_scatter['Return time'] == i)].count()
        dict_list_yearly.append(dict_for_yearly.copy())

df = pd.DataFrame.from_records(dict_list_yearly)
df_sorted_yearly = df.sort_values(['Year', 'Return years']).reset_index()
df_sorted_yearly.loc[df_sorted_yearly['Count'] > 0, 'Return tax'] = df_sorted_yearly.loc[df_sorted_yearly['Count'] > 0, 'Return years']
df_sorted_yearly.loc[df_sorted_yearly['Count'] == 0, 'Count'] = np.nan
df_sorted_yearly['Max Return'] = df_sorted_yearly['Year'].max() - df_sorted_yearly['Year']
df_sorted_yearly['Cum years'] = df_sorted_yearly['Return years'] * df_sorted_yearly['Count']
df_sorted_yearly['Mean'] = np.nan
df_sorted_yearly['Mean'] = round(df_sorted_yearly.loc[df_sorted_yearly['Return tax'] > 0].groupby(df_sorted_yearly['Year'])['Cum years'].transform('sum')/df_sorted_yearly.loc[df_sorted_yearly['Return tax'] > 0].groupby(df_sorted_yearly['Year'])['Count'].transform('sum'),2)
ax_scatter_years = sns.scatterplot(df_sorted_yearly, x='Year', y='Return tax', size='Count', sizes=(40, 400), alpha=.5, legend='brief')
ax_scatter_years = sns.lineplot(df_sorted_yearly, x='Year', y='Max Return')
ax_scatter_years = sns.regplot(df_sorted_yearly, x='Year', y='Mean')
leg = plt.legend(loc='upper right', labels=['Max return years', 'Regression', 'Nº of Events'])
ax_scatter_years.add_artist(leg)
plt.legend(loc=[0.8, 0.5])
ax_scatter_years.set(ylabel='Return Years')

for reg in df_scatter['sub-ecoregion'].unique():
    plt.clf()
    df_reg = df_scatter.loc[df_scatter['sub-ecoregion'] == reg]
    dict_list_yearly = []
    if (reg == 'Ionian Sea') | (reg == 'Tunisian Plateau-Gulf of Sidra'):
        print('hey')
    for i in range(1, 41):
        for year in df_reg['Year'].unique():
            dict_for_yearly['Year'] = year
            dict_for_yearly['Return years'] = i
            dict_for_yearly['Count'] = df_reg['Return time'].loc[
                (df_reg['Year'] == year) & (df_reg['Return time'] == i)].count()
            dict_list_yearly.append(dict_for_yearly.copy())

    df = pd.DataFrame.from_records(dict_list_yearly)
    df_sorted_yearly = df.sort_values(['Year', 'Return years']).reset_index()
    df_sorted_yearly.loc[df_sorted_yearly['Count'] > 0, 'Return tax'] = df_sorted_yearly.loc[
        df_sorted_yearly['Count'] > 0, 'Return years']
    df_sorted_yearly.loc[df_sorted_yearly['Count'] == 0, 'Count'] = np.nan
    df_sorted_yearly['Max Return'] = df_sorted_yearly['Year'].max() - df_sorted_yearly['Year']
    df_sorted_yearly['Cum years'] = df_sorted_yearly['Return years'] * df_sorted_yearly['Count']
    df_sorted_yearly['Mean'] = np.nan
    df_sorted_yearly['Mean'] = round(
        df_sorted_yearly.loc[df_sorted_yearly['Return tax'] > 0].groupby(df_sorted_yearly['Year'])[
            'Cum years'].transform('sum') /
        df_sorted_yearly.loc[df_sorted_yearly['Return tax'] > 0].groupby(df_sorted_yearly['Year'])['Count'].transform(
            'sum'), 2)
    ax_scatter_years2 = sns.scatterplot(df_sorted_yearly, x='Year', y='Return tax', size='Count', sizes=(40, 400),
                                       alpha=.5, legend='brief')
    ax_scatter_years2 = sns.lineplot(df_sorted_yearly, x='Year', y='Max Return')
    ax_scatter_years2 = sns.regplot(df_sorted_yearly, x='Year', y='Mean', ci=None)
    leg = plt.legend(loc='upper right', labels=['Max return years', 'Regression', 'Nº of Events'])
    ax_scatter_years2.add_artist(leg)
    plt.legend(loc=[0.8, 0.3])
    plt.title(reg)
    ax_scatter_years2.set(ylabel='Return Years')
    plt.savefig('../src/output_images/RT_Reg_' + reg + '.png',
                bbox_inches='tight')
    print('ha')




dict_for_df = {'Decade' : '', 'Return years' : 0, 'Count' : 0}
dec_sum = 0
oldi_year = 0
dict_list = []
for i in range(1, 11):
    for year in df_scatter['Year'].unique():
        if oldi_year == 0:
            oldi_year = year
        dec_sum = df_scatter['Return time'].loc[(df_scatter['Year'] == year) & (df_scatter['Return time'] == i)].count() + dec_sum
        if year-10 == round(oldi_year/10)*10:
            dict_for_df['Decade'] = str(oldi_year) + '-' + str(year)
            dict_for_df['Return years'] = i
            dict_for_df['Count'] = dec_sum
            dict_list.append(dict_for_df.copy())
            oldi_year = 0
            dec_sum = 0

df = pd.DataFrame.from_records(dict_list)
df_sorted = df.sort_values(['Decade', 'Return years']).reset_index()
df_sorted['Cum years'] = df_sorted['Return years'] * df_sorted['Count']
df_sorted['Total record decade'] = df_sorted.groupby(df_sorted['Decade'])['Count'].transform('sum')
df_sorted['Mean'] = round(df_sorted.groupby(df_sorted['Decade'])['Cum years'].transform('sum')/df_sorted['Total record decade'],2)

df_sorted['Return records'] = np.nan
df_sorted['Return records'].loc[df_sorted['Count'] > 0] = df_sorted['Return years'].loc[df_sorted['Count'] > 0]
df_sorted.to_csv('Sorted data.txt', sep='\t')
ax = sns.catplot(x = "Return years",       # x variable name
            y = "Count",       # y variable name
            hue = "Decade",  # group variable name
            data = df_sorted,     # dataframe to plot
            kind = "bar").set(xlabel='Return years', ylabel='No. of Records')

sns.scatterplot(df_sorted, x='Decade', y='Mean')

df_sorted.to_csv('Sorted data.txt', sep='\t')
print('ye')