import numpy as np
import pandas as pd
import scipy as sp

from matplotlib import pyplot as plt

data = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202210.txt', sep="\t")

data2 = data.drop(['Time', '10', '15', '20', '25', '30', '35', '40'], axis=1)

data2['Date'] = pd.to_datetime(data2['Date'], dayfirst=True)
data2.insert(1, 'day', pd.DatetimeIndex(data2['Date']).day)
data2.insert(2, 'month', pd.DatetimeIndex(data2['Date']).month)
data2.insert(3, 'year', pd.DatetimeIndex(data2['Date']).year)

last_years_means = data2.loc[data2['year']!= data2['year'].max()].groupby(['day', 'month'], as_index=False).mean().rename(columns={'5':str(data2['year'].min()) +'-'+str(data2['year'].max()-1)}).drop('year', axis=1)
last_years_means.sort_values(['month', 'day'], inplace=True)
last_years_means['date'] = pd.to_datetime('2020/' + last_years_means["month"].astype(str) + "/" + last_years_means["day"].astype(str))
last_years_means.set_index('date', inplace=True)
last_years_means.drop(['month', 'day'], axis=1, inplace=True)

last_years_percentile = data2.loc[data2['year']!= data2['year'].max()].groupby(['day', 'month'], as_index=False).quantile(.9).rename(columns={'5':str(data2['year'].min()) +'-'+str(data2['year'].max()-1)+'p90'}).drop(['year', 'Date'], axis=1)
last_years_percentile.sort_values(['month', 'day'], inplace=True)
last_years_percentile['date'] = pd.to_datetime('2020/' + last_years_percentile["month"].astype(str) + "/" + last_years_percentile["day"].astype(str))
last_years_percentile.set_index('date', inplace=True)
last_years_percentile.drop(['month', 'day'], axis=1, inplace=True)

this_year_mean = data2.loc[data2['year']== data2['year'].max()].groupby(['day', 'month'], as_index=False).mean().rename(columns={'5':str(data2['year'].max())}).drop('year', axis=1)
this_year_mean.sort_values(['month', 'day'], inplace=True)
this_year_mean['date'] = pd.to_datetime('2020/' + this_year_mean["month"].astype(str) + "/" + this_year_mean["day"].astype(str))
this_year_mean.set_index('date', inplace=True)
this_year_mean.drop(['month', 'day'], axis=1, inplace=True)

concated = pd.concat([last_years_means, last_years_percentile, this_year_mean], axis=1)
#concated.index = concated.index.strftime('%b')

ax = plt.axes()
cycler = plt.cycler(linestyle=['-', '--', '-'], color=['red', 'red', 'black'],)
ax.set_prop_cycle(cycler)
concated.plot(ax=ax)
plt.fill_between(concated.index, concated['2002-2021p90'], concated['2022'], where=(concated['2022']>concated['2002-2021p90']), color='yellow')

# TODO hacer esto automatico para cada profundidad de un site en concreto // copiar los colores de marinheatwaves
print('hola')