import numpy as np
import pandas as pd
import scipy as sp
from scipy.ndimage.filters import uniform_filter1d

from matplotlib import pyplot as plt
import matplotlib.patches as mpatches




def marine_heat_spikes_plotter(data, depth):
    # Sets the time columns
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    data.insert(1, 'day', pd.DatetimeIndex(data['Date']).day)
    data.insert(2, 'month', pd.DatetimeIndex(data['Date']).month)
    data.insert(3, 'year', pd.DatetimeIndex(data['Date']).year)

    # Gets the names of the legends
    first_year = str(data['year'].min())
    second2last_year = str(data['year'].max() - 1)
    last_year = str(data['year'].max())
    last_years_legend = first_year + '-' + second2last_year
    percentile_legend = first_year + '-' + second2last_year + ' p90'
    this_year_legend = last_year

    # Filter the data for 15 days
    last_years_filtered = pd.DataFrame(uniform_filter1d(data[depth].dropna(), size=360),
                                       index=data[depth].dropna().index, columns=[depth]).reindex(data.index)
    last_years_filtered['Date'] = data['Date']
    last_years_filtered['year'] = data['year']
    last_years_filtered['month'] = data['month']
    last_years_filtered['day'] = data['day']

    # Creates the Dataframe for the last years
    last_years_means = last_years_filtered.loc[
        last_years_filtered['year'] != last_years_filtered['year'].max()].groupby(['day', 'month'],
                                                                                  as_index=False).mean().rename(
        columns={depth: last_years_legend}).drop('year', axis=1)
    last_years_means.sort_values(['month', 'day'], inplace=True)
    last_years_means['date'] = pd.to_datetime(
        '2020/' + last_years_means["month"].astype(str) + "/" + last_years_means["day"].astype(str))
    last_years_means.set_index('date', inplace=True)
    last_years_means.drop(['month', 'day'], axis=1, inplace=True)

    # Creates the Dataframe for the percentile
    last_years_percentile = last_years_filtered.loc[
        last_years_filtered['year'] != last_years_filtered['year'].max()].groupby(['day', 'month'],
                                                                                  as_index=False).quantile(.9).rename(
        columns={depth: percentile_legend}).drop(['year', 'Date'], axis=1)
    last_years_percentile.sort_values(['month', 'day'], inplace=True)
    last_years_percentile['date'] = pd.to_datetime(
        '2020/' + last_years_percentile["month"].astype(str) + "/" + last_years_percentile["day"].astype(str))
    last_years_percentile.set_index('date', inplace=True)
    last_years_percentile.drop(['month', 'day'], axis=1, inplace=True)

    # Creates the Dataframe for this year
    this_year_mean = data.loc[data['year'] == data['year'].max()].groupby(['day', 'month'],
                                                                             as_index=False).mean().rename(
        columns={depth: this_year_legend}).drop('year', axis=1)
    this_year_mean.sort_values(['month', 'day'], inplace=True)
    this_year_mean['date'] = pd.to_datetime(
        '2020/' + this_year_mean["month"].astype(str) + "/" + this_year_mean["day"].astype(str))
    this_year_mean.set_index('date', inplace=True)
    this_year_mean.drop(['month', 'day'], axis=1, inplace=True)

    # Sets a unique Dataframe consisting of the other three
    concated = pd.concat([last_years_means, last_years_percentile, this_year_mean], axis=1)
    prop = concated.index.strftime('%b')
    concated.index = concated.index.strftime('%m-%d')

    # Starts the axes and plots the data
    ax = plt.axes()
    cycler = plt.cycler(linestyle=['-', '--', '-'], color=['#a62929', '#a62929', '#141414'], )
    ax.set_prop_cycle(cycler)
    concated.plot(ax=ax)
    plt.fill_between(concated.index, concated[percentile_legend], concated[this_year_legend],
                     where=(concated[this_year_legend] > concated[percentile_legend]), color='#ff9507')
    plt.xlabel('')
    plt.xticks(
        ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01', '12-01'])
    plt.xlim((concated.index[0], concated.index[-1]))
    ax.set_xticklabels(prop.unique())

    # Sets the legend in order to include the fill_between value
    fill_patch = mpatches.Patch(color='#ff9507', label='Marine heat spike')
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles=handles + [fill_patch])
    plt.title('Daily sea temperature in XXX at ' + depth + ' meters deep')
    plt.savefig('../src/output_images/spike_XXX_' + depth + '.png')
    ax.remove()


# Opens the data
dataset = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202210.txt', sep="\t")
data2 = dataset.drop(['Time'], axis=1)

for depth in data2.columns[1:]:
    marine_heat_spikes_plotter(pd.DataFrame(data2, columns=['Date', depth]), depth)
# TODO hacer esto automatico para cada profundidad de un site en concreto // copiar los colores de marinheatwaves
print('hola')
