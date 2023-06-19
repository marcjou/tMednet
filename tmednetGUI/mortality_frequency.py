import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MME_Plot:

    def __init__(self, PATH):
        self.df_events = pd.read_excel('../src/MME.xlsx', sheet_name='Quim Years with MME')
        self.df_numbers = pd.read_excel('../src/MME.xlsx', sheet_name='Massimo original dataset')
        self.df_events.columns = self.df_events.columns.astype(str)
        self.columns = self.df_events.columns

    def plot_affected_percentage(self):
        df_inc = pd.DataFrame([self.df_events['#Years with MME'].loc[self.df_events['#Years with MME'] == i].count() for i in y_axis],
                              columns=['count'])
        df_inc['% affected'] = (df_inc['count'] / total_hex) * 100
        df_inc['N affected'] = df_inc['count']
        df_inc['y_axis'] = y_axis
        ax = df_inc.plot.bar(x='y_axis', y='% affected')
        ax.set_xlabel('Years with MME')
        ax.set_ylabel('Percentage of affected hexagons')
        ax.set_ylim([0, 100])
        plt.xticks(rotation=0)
        ax.get_legend().remove()
        plt.title('Mediterranean MME')
        self.save_image('MME_Global')

    def save_image(self, title):
        plt.savefig('../src/output_images/' + title + '.png',
                    bbox_inches='tight')

    def affected_percentage_regional_composer(self):
        self.loop_ecoregion(self.plot_affected_percentage_regional)

    def loop_ecoregion(self, func):
        for n in self.df_events['sub-ecoregion'].unique():
            func(n)

    def plot_affected_percentage_regional(self, reg):
        y_axis = self.df_events['#Years with MME'].loc[self.df_events['sub-ecoregion'] == reg].unique()
        y_axis.sort()
        total_hex = self.df_events['#Years with MME'].loc[self.df_events['sub-ecoregion'] == reg].count()
        df_inc = pd.DataFrame(
            [self.df_events['#Years with MME'].loc[(self.df_events['#Years with MME'] == i) & (self.df_events['sub-ecoregion'] == reg)].count() for i in
             y_axis],
            columns=['count'])
        df_inc['% affected'] = (df_inc['count'] / total_hex) * 100
        df_inc['N affected'] = df_inc['count']
        df_inc['y_axis'] = y_axis
        ax = df_inc.plot.bar(x='y_axis', y='% affected')
        ax.set_xlabel('Years with MME')
        ax.set_ylabel('Percentage of affected hexagons')
        ax.set_ylim([0, 100])
        plt.xticks(rotation=0)
        ax.get_legend().remove()
        plt.title(reg + ' MME')
        self.save_image('MME_' + reg)


'''

ex = pd.read_excel('../src/MME.xlsx', sheet_name='Quim Years with MME')
ex.columns = ex.columns.astype(str)
columns = ex.columns[4:]

df_third = pd.DataFrame(columns, columns=['Year'])
df_third['Count'] = 0
for year in columns:
    df_third['Count'].loc[df_third['Year'] == year] = ex[year].sum()
y_axis = ex['#Years with MME'].unique()
y_axis.sort()
total_hex = ex['#Years with MME'].count()

#Dataframe for counting N of MME per

df_third['Year'] = df_third['Year'].astype(int)
ax = df_third.plot.bar(x='Year', y='Count', figsize = (10, 5))
ax.set_xlabel('Year')
ax.set_ylabel('Number of affected hexagons')
ax.set_ylim([0, df_third['Count'].max() + 25])
plt.xticks(rotation=90)
ax.get_legend().remove()
plt.title('Mediterranean MME')
plt.savefig('../src/output_images/MME_N_Global.png',
                                bbox_inches='tight')
for n in ex['sub-ecoregion'].unique():
    y_axis = ex['#Years with MME'].loc[ex['sub-ecoregion'] == n].unique()
    y_axis.sort()
    total_hex = ex['#Years with MME'].loc[ex['sub-ecoregion'] == n].count()
    df_inc = pd.DataFrame([ex['#Years with MME'].loc[(ex['#Years with MME'] == i) & (ex['sub-ecoregion'] == n)].count() for i in y_axis],
                          columns=['count'])
    df_inc['% affected'] = (df_inc['count'] / total_hex) * 100
    df_inc['N affected'] = df_inc['count']
    df_inc['y_axis'] = y_axis
    ax = df_inc.plot.bar(x='y_axis', y='% affected')
    ax.set_xlabel('Years with MME')
    ax.set_ylabel('Percentage of affected hexagons')
    ax.set_ylim([0, 100])
    plt.xticks(rotation=0)
    ax.get_legend().remove()
    plt.title(n + ' MME')
    plt.savefig('../src/output_images/MME_' + n + '.png',
                bbox_inches='tight')

    for year in columns:
        df_third['Count'].loc[df_third['Year'] == year] = ex[year].loc[ex['sub-ecoregion'] == n].sum()
    ax = df_third.plot.bar(x='Year', y='Count', figsize = (10, 5))
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of affected hexagons')
    ax.set_ylim([0, df_third['Count'].max() + 25])
    plt.xticks(rotation=90)
    ax.get_legend().remove()
    plt.title(n + ' MME')
    plt.savefig('../src/output_images/MME_N_' + n + '.png',
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
ax2 = df_scatter.plot.scatter(x='Year', y='Return time')
ax2.set_xlabel('Year')
ax2.set_ylabel('Number of years to return')
ax2.set_ylim([0, 40])
ax2.set_xlim([1978, 2020])
plt.title('Mediterranean Return Time')
plt.savefig('../src/output_images/RT_Global.png', bbox_inches='tight')

#Create a list of decades
decade_list = []
i = df_scatter['Year'].unique()[0]
while i < df_scatter['Year'].unique()[-1]:
    new_i = round((i + 10) / 10) * 10
    decade_list.append(str(i) + '-' + str(new_i))
    i = new_i + 1

dict_for_df = {'Decade' : '', 'Return years' : 0, 'Count' : 0}
dec_sum = 0
oldi_year = 0
for i in range(1, 11):
    for year in df_scatter['Year'].unique():
        if oldi_year == 0:
            oldi_year = year
        dec_sum = df_scatter['Return time'].loc[(df_scatter['Year'] == year) & (df_scatter['Return time'] == i)].count() + dec_sum
        if year-10 == round(oldi_year/10)*10:
            dict_for_df['Decade'] = str(oldi_year) + '-' + str(year)
            dict_for_df['Return years'] = i
            dict_for_df['Count'] = dec_sum

dec_sum = dict.fromkeys(df_scatter['Year'].unique(), 0)
for year in df_scatter['Year'].unique():
    for i in range(1, 11):
        dec_sum[year] = df_scatter.loc[(df_scatter['Year'] == year) & (df_scatter['Return time'] == i)].count() + dec_sum


for n in ex['sub-ecoregion'].unique():
    ux = ex.loc[ex['sub-ecoregion'] == n]
    df_return = ux.copy()
    ret_counter = 0
    old_year = ''
    for idx, row in ux.iterrows():
        for year in columns:
            if row[year] == 1 or year == columns[-1]:
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
    ax2 = df_scatter.plot.scatter(x='Year', y='Return time')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Number of years to return')
    ax2.set_ylim([0, 40])
    ax2.set_xlim([1978, 2020])
    plt.title(n + 'Return Time')
    plt.savefig('../src/output_images/RT_' + n + '.png',
                bbox_inches='tight')

print('stop')

'''