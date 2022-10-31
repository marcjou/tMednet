import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from scipy.ndimage.filters import uniform_filter1d


def marine_heat_spikes_setter(data, target_year, clim=False):
    # Sets the time columns
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    data.insert(1, 'day', pd.DatetimeIndex(data['Date']).day)
    data.insert(2, 'month', pd.DatetimeIndex(data['Date']).month)
    data.insert(3, 'year', pd.DatetimeIndex(data['Date']).year)

    # Gets the names of the legends
    first_year = str(data['year'].min())
    second2last_year = str(target_year - 1)
    last_year = str(target_year)
    last_years_legend = first_year + '-' + second2last_year
    percentile_legend = first_year + '-' + second2last_year + ' p90'
    low_percentile_legend = first_year + '-' + second2last_year + ' p10'
    this_year_legend = last_year
    if clim:
        last_years_legend = last_years_legend + ' Climatology'
    return data, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend


def marine_heat_spikes_filter(data, depth):
    # Filter the data for 15 days
    last_years_filtered = pd.DataFrame(uniform_filter1d(data[depth].dropna(), size=360),
                                       index=data[depth].dropna().index, columns=[depth]).reindex(data.index)
    last_years_filtered['Date'] = data['Date']
    last_years_filtered['year'] = data['year']
    last_years_filtered['month'] = data['month']
    last_years_filtered['day'] = data['day']

    return last_years_filtered


def marine_heat_spikes_df_setter(data, depth, legend, target_year, type='mean', years='old', percentile=0):
    if years == 'old':
        locator = data['year'] < target_year
    else:
        locator = data['year'] == target_year
    if type=='mean':
        df = data.loc[locator].groupby(['day', 'month'], as_index=False).mean().rename(
            columns={depth: legend}).drop('year', axis=1)
    if type=='percentile':
        df = data.loc[locator].groupby(['day', 'month'], as_index=False).quantile(percentile).rename(
            columns={depth: legend}).drop(['year', 'Date'], axis=1)
    if type=='minmax':
        df = data.loc[locator].groupby(['day', 'month'], as_index=False).min().rename(
            columns={depth: 'min'}).drop(['year', 'Date'], axis=1)
        df['max'] = data.loc[locator].groupby(['day', 'month'], as_index=False).max().rename(
            columns={depth: 'max'}).drop(['year', 'Date'], axis=1)['max']
    df.sort_values(['month', 'day'], inplace=True)
    df['date'] = pd.to_datetime(
        '2020/' + df["month"].astype(str) + "/" + df["day"].astype(str))
    df.set_index('date', inplace=True)
    df.drop(['month', 'day'], axis=1, inplace=True)

    return df

def spike_plot_setter(data, prop, target_year, sitename, depth, percentile_legend, this_year_legend):
    # Starts the axes and plots the data
    ax = plt.axes()
    cycler = plt.cycler(linestyle=['-', '--', '--', '-', '-', '-', '-'],
                        color=['#a62929', '#a62929', 'blue', '#141414', 'blue', 'blue', 'blue'],
                        alpha=[1., 1., 0., 1., 0., 0., 0.])
    ax.set_prop_cycle(cycler)
    data.plot(ax=ax)

    # #ff9507 color of the fill_between classic
    plt.fill_between(data.index, data[percentile_legend], data[this_year_legend],
                     where=(data[this_year_legend] > data[percentile_legend]), color='#f8e959')
    plt.fill_between(data.index, data['x2'], data[this_year_legend],
                     where=(data[this_year_legend] > data['x2']), color='#f66000')
    plt.fill_between(data.index, data['x3'], data[this_year_legend],
                     where=(data[this_year_legend] > data['x3']), color='#ce2200')
    plt.fill_between(data.index, data['x4'], data[this_year_legend],
                     where=(data[this_year_legend] > data['x4']), color='#810000')
    # plt.fill_between(concated.index, concated[low_percentile_legend], concated[this_year_legend],
    #                 where=(concated[this_year_legend] < concated[low_percentile_legend]), color='#c7ecf2')
    plt.xlabel('')
    plt.xticks(
        ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01', '12-01'])
    plt.xlim((data.index[0], data.index[-1]))
    ax.set_xticklabels(prop.unique())

    # Sets the legend in order to include the fill_between value
    fill_patch = mpatches.Patch(color='#f8e959', label='Moderate')
    spike2_patch = mpatches.Patch(color='#f66000', label='Strong')
    spike3_patch = mpatches.Patch(color='#ce2200', label='Severe')
    spike4_patch = mpatches.Patch(color='#810000', label='Extreme')
    low_patch = mpatches.Patch(color='#c7ecf2', label='Marine low spike')
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles=handles[:2] + [handles[3]] + [fill_patch, spike2_patch, spike3_patch, spike4_patch])
    plt.title(str(target_year) + ' Marine HeatWaves in ' + sitename + ' at ' + depth + ' meters deep')
    plt.savefig('../src/output_images/' + str(target_year) + '_spike_' + sitename + ' ' + depth + '.png')
    ax.remove()

def spike_zoom_setter(data, prop, target_year, sitename, depth, percentile_legend, this_year_legend):
    # Plot the zoom for summer
    prop_zoom = prop.to_list()
    prop_zoom = pd.Index(prop_zoom[prop_zoom.index('Jun'):prop_zoom.index('Oct')])
    concated_zoom = data.loc['06-01':'10-01'][:-1]
    ax = plt.axes()
    cycler = plt.cycler(linestyle=['-', '--', '--', '-', '-', '-', '-'],
                        color=['#a62929', '#a62929', 'blue', '#141414', 'blue', 'blue', 'blue'],
                        alpha=[1., 1., 0., 1., 0., 0., 0.])
    ax.set_prop_cycle(cycler)
    concated_zoom.plot(ax=ax)

    plt.fill_between(concated_zoom.index, concated_zoom[percentile_legend], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] > concated_zoom[percentile_legend]), color='#f8e959')
    plt.fill_between(concated_zoom.index, concated_zoom['x2'], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] > concated_zoom['x2']), color='#f66000')
    plt.fill_between(concated_zoom.index, concated_zoom['x3'], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] > concated_zoom['x3']), color='#ce2200')
    plt.fill_between(concated_zoom.index, concated_zoom['x4'], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] > concated_zoom['x4']), color='#810000')

    plt.xlabel('')
    plt.xticks(
        ['06-01', '07-01', '08-01', '09-01'])
    plt.xlim((concated_zoom.index[0], concated_zoom.index[-1]))
    ax.set_xticklabels(prop_zoom.unique())
    # Sets the legend in order to include the fill_between value
    fill_patch = mpatches.Patch(color='#f8e959', label='Moderate')
    spike2_patch = mpatches.Patch(color='#f66000', label='Strong')
    spike3_patch = mpatches.Patch(color='#ce2200', label='Severe')
    spike4_patch = mpatches.Patch(color='#810000', label='Extreme')
    low_patch = mpatches.Patch(color='#c7ecf2', label='Marine low spike')
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles=handles[:2] + [handles[3]] + [fill_patch, spike2_patch, spike3_patch, spike4_patch])
    plt.title(str(target_year) + ' Marine HeatWaves in Summer in ' + sitename + ' at ' + depth + ' meters deep')
    plt.savefig('../src/output_images/' + str(target_year) + '_spike_Summer Months_' + sitename + '_' + depth + '.png')
    ax.remove()


def marine_heat_spikes_plotter(data, depth, sitename, target_year):
    data, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend = marine_heat_spikes_setter(
        data, target_year)
    last_years_filtered = marine_heat_spikes_filter(data, depth)
    last_years_means = marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year)
    last_years_percentile = marine_heat_spikes_df_setter(last_years_filtered, depth, percentile_legend, target_year,type='percentile', percentile=.9)
    this_year_mean = marine_heat_spikes_df_setter(data, depth, this_year_legend, target_year, years='new')
    low_percentile = marine_heat_spikes_df_setter(last_years_filtered, depth, low_percentile_legend, target_year,type='percentile', percentile=.1)
    # Sets a unique Dataframe consisting of the other
    concated = pd.concat([last_years_means, last_years_percentile, low_percentile, this_year_mean], axis=1)
    prop = concated.index.strftime('%b')
    concated.index = concated.index.strftime('%m-%d')

    # Now it's time to set the categories of the spikes, which are multiples of the difference between the climatology
    # and the p90

    difference = concated[percentile_legend] - concated[last_years_legend]
    concated['x2'] = difference * 2 + concated[last_years_legend]
    concated['x3'] = difference * 3 + concated[last_years_legend]
    concated['x4'] = difference * 4 + concated[last_years_legend]
    spike_plot_setter(concated, prop, target_year, sitename, depth, percentile_legend, this_year_legend)
    spike_zoom_setter(concated, prop, target_year, sitename, depth, percentile_legend, this_year_legend)


def anomaly_plot_setter(data, prop, sitename, target_year, depth, last_years_legend, this_year_legend):
    ax = plt.axes()
    cycler = plt.cycler(linestyle=['-', '-', '--', '--'], color=['black', 'grey', '#01086b', '#820316'], alpha=[1., 0.7, 1., 1.], linewidth=[0.7, 0.7, 0.7, 0.7])
    ax.set_prop_cycle(cycler)
    data.plot(ax=ax)

    plt.fill_between(data.index, data[last_years_legend], data[this_year_legend],
                     where=(data[this_year_legend] > data[last_years_legend]), color='#fa5a5a')
    plt.fill_between(data.index, data[last_years_legend], data[this_year_legend],
                     where=(data[this_year_legend] < data[last_years_legend]), color='#5aaaff')

    plt.xlabel('')
    plt.xticks(
        ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01', '12-01'])
    plt.xlim((data.index[0], data.index[-1]))
    ax.set_xticklabels(prop.unique())

    plt.title(str(target_year) + ' Anomalies in ' + sitename + ' at ' + depth + ' meters deep')
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles=[handles[0], handles[2], handles[3]], labels=[labels[0]] + ['Historic min.', 'Historic max.'])
    plt.savefig('../src/output_images/' + str(target_year) + '_anomalies_' + sitename + '_' + depth + '.png')
    ax.remove()


def anomaly_zoom_setter(data, prop, sitename, target_year, depth, last_years_legend, this_year_legend):
    # Plot the zoom for summer
    prop_zoom = prop.to_list()
    prop_zoom = pd.Index(prop_zoom[prop_zoom.index('Jun'):prop_zoom.index('Oct')])
    concated_zoom = data.loc['06-01':'10-01'][:-1]
    anomaly = pd.DataFrame(concated_zoom[this_year_legend] - concated_zoom[last_years_legend],
                           index=concated_zoom.index,
                           columns=['anomaly'])
    anomaly['zero'] = 0
    ax = plt.axes()
    cycler = plt.cycler(linestyle=['-', '-', '--', '--'], color=['black', 'grey', '#01086b', '#820316'], alpha=[1., 0.7, 1., 1.], linewidth=[0.7, 0.7, 0.7, 0.7])
    ax.set_prop_cycle(cycler)
    concated_zoom.plot(ax=ax)

    plt.fill_between(concated_zoom.index, concated_zoom[last_years_legend], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] > concated_zoom[last_years_legend]), color='#fa5a5a')
    plt.fill_between(concated_zoom.index, concated_zoom[last_years_legend], concated_zoom[this_year_legend],
                     where=(concated_zoom[this_year_legend] < concated_zoom[last_years_legend]), color='#5aaaff')

    plt.xlabel('')
    plt.xticks(
        ['06-01', '07-01', '08-01', '09-01'])
    plt.xlim((concated_zoom.index[0], concated_zoom.index[-1]))
    ax.set_xticklabels(prop_zoom.unique())

    plt.title(str(target_year) + ' Anomalies in Summer in ' + sitename + ' at ' + depth + ' meters deep')
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles=[handles[0], handles[2], handles[3]], labels=[labels[0]] + ['Historic min.', 'Historic max.'])
    plt.savefig(
        '../src/output_images/' + str(target_year) + '_anomalies_Summer Months_' + sitename + '_' + depth + '.png')
    ax.remove()

#def get_max_and_min(data):

def anomalies_plotter(data, depth, sitename, target_year):
    data, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend = marine_heat_spikes_setter(
        data, target_year, clim=True)
    last_years_filtered = marine_heat_spikes_filter(data, depth)
    last_years_means = marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year)
    this_year_mean = marine_heat_spikes_df_setter(data, depth, this_year_legend, target_year, years='new')
    min_max_temp = marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year, type='minmax')
    # Sets a unique Dataframe consisting of the other three
    concated = pd.concat([last_years_means, this_year_mean, min_max_temp], axis=1)
    prop = concated.index.strftime('%b')
    concated.index = concated.index.strftime('%m-%d')
    anomaly = pd.DataFrame(concated[this_year_legend] - concated[last_years_legend], index=concated.index,
                           columns=['anomaly'])
    anomaly['zero'] = 0
    anomaly_plot_setter(concated, prop, sitename, target_year, depth, last_years_legend, this_year_legend)
    anomaly_zoom_setter(concated, prop, sitename, target_year, depth, last_years_legend, this_year_legend)


# Opens the data
# dataset = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202210.txt', sep="\t")
# data2 = dataset.drop(['Time'], axis=1)


def browse_heat_spikes(data, sitename, year):
    data = data.drop(['Time'], axis=1)
    for depth in data.columns[1:]:
        marine_heat_spikes_plotter(pd.DataFrame(data, columns=['Date', depth]), depth, sitename, year)


def browse_anomalies(data, sitename, year):
    data = data.drop(['Time'], axis=1)
    for depth in data.columns[1:]:
        anomalies_plotter(pd.DataFrame(data, columns=['Date', depth]), depth, sitename, year)

# browse_heat_spikes(dataset)
