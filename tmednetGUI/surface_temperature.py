import pandas as pd
import numpy as np
from labellines import labelLine
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from scipy.ndimage.filters import uniform_filter1d
from datetime import datetime


class HistoricData:
    """
    Creates an object that contains the data of the Database_T files in a dataframe structure
    giving it also different functionalities as calculating and plotting the anomalies or
    heat spikes

    ...

    Attributes
    ----------
    df : pandas DataFrame
        DataFrame containing all the information included on the Database_T file
    site_name : str
        Name of the site where the data comes from
    max_temperature : int
        Max temperature reached at the site at any depth from start to finish of the series
    last_year : int
        Last year of recorded operation plus 1 to calculate the ranges

    Methods
    -------
    browse_anomalies(year)
        Plots the anomalies for all the depths of the series on a given year

    browse_heat_spikes(year)
        Plots the heat spikes for all the depths of the series on a given year

    anomalies_plotter(data, depth, year)
        Plots the anomalies for a given depth on a given year

    multidepth_anomaly_plotter(year, depths=['10', '25', '40'])
        Plots the anomalies for a set of three depths of the series on a given year

    marine_heat_spikes_plotter(data, depth, target_year)
        Plots the heat spikes for a given depth on a given year

    Version: 03/2023 MJB: Documentation
    """
    def __init__(self, filename):
        """
        Parameters
        ----------
        filename: str
            The complete path to the Database_T file containing the historic data
        """
        self.df = pd.read_csv(filename, sep='\t')
        self.site_name = filename[filename.find('Database'):].split('_')[3]
        self.max_temperature = round(np.max(self.df.quantile(0.99, numeric_only=True))) + 1
        self.last_year = datetime.strptime(self.df['Date'][len(self.df) - 1], '%d/%m/%Y').year + 1

    def __str__(self):
        return "Dataset of {}".format(self.site_name)

    @staticmethod
    def __marine_heat_spikes_setter(data, target_year, clim=False):
        # Modifies the data parameter adding day, month and year columns as well as setting the names
        # Of the legends

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

    @staticmethod
    def __marine_heat_spikes_filter(data, depth):
        # Filters the data using a uniform1d filter
        not_null_index = data.loc[data[depth].notnull()].index
        oldindex = not_null_index[0]
        end_index = []
        start_index = []
        df_filtered = []
        for i in not_null_index:
            hueco = i - oldindex
            if hueco <= 24:
                oldindex = i
            else:
                end_index.append(oldindex)
                start_index.append(i)
                oldindex = i
        if len(end_index) > 0:
            for i in range(0, len(end_index)):
                if i == 0:
                    last_years_filtered = pd.DataFrame(
                        uniform_filter1d(data[depth].loc[i:end_index[i]].dropna(), size=360),
                        index=data[depth].loc[i:end_index[i]].dropna().index, columns=[depth]).reindex(
                        data.loc[i:end_index[i]].index)
                    df_filtered = last_years_filtered.copy()
                elif i == (len(end_index) - 1):
                    last_years_filtered = pd.DataFrame(
                        uniform_filter1d(data[depth].loc[start_index[i]: len(data) - 1].dropna(), size=360),
                        index=data[depth].loc[start_index[i]: len(data) - 1].dropna().index,
                        columns=[depth]).reindex(data.loc[start_index[i]: len(data) - 1].index)
                    df_filtered = pd.concat([df_filtered, last_years_filtered], axis=0, join='outer')
                else:
                    last_years_filtered = pd.DataFrame(
                        uniform_filter1d(data[depth].loc[start_index[i]: end_index[i + 1]].dropna(), size=360),
                        index=data[depth].loc[start_index[i]: end_index[i + 1]].dropna().index,
                        columns=[depth]).reindex(data.loc[start_index[i]: end_index[i + 1]].index)
                    df_filtered = pd.concat([df_filtered, last_years_filtered], axis=0, join='outer')
        else:

            # Filter the data for 15 days
            df_filtered = pd.DataFrame(uniform_filter1d(data[depth].dropna(), size=360),
                                       index=data[depth].dropna().index, columns=[depth]).reindex(data.index)

        df_filtered = df_filtered.reindex(data.index)
        df_filtered['Date'] = data['Date']
        df_filtered['year'] = data['year']
        df_filtered['month'] = data['month']
        df_filtered['day'] = data['day']

        return df_filtered

    @staticmethod
    def __marine_heat_spikes_df_setter(data, depth, legend, target_year, type='mean', years='old', percentile=0):
        # Creates a new dataframe from the one passed from the data parameter that can contain the min and max,
        # the percentile or the mean of the data
        df = []
        if years == 'old':
            locator = data['year'] < target_year
        else:
            locator = data['year'] == target_year
        if type == 'mean':
            df = data.loc[locator].groupby(['day', 'month'], as_index=False).mean(numeric_only=True).rename(
                columns={depth: legend}).drop('year', axis=1)
            if 'Date' in df:
                df.drop('Date', axis=1)
        if type == 'percentile':
            df = data.loc[locator].groupby(['day', 'month'], as_index=False).quantile(percentile, numeric_only=True).rename(
                columns={depth: legend}).drop(['year'], axis=1)
            if 'Date' in df:
                df.drop('Date', axis=1, inplace=True)
        if type == 'minmax':
            df = data.loc[locator].groupby(['day', 'month'], as_index=False).min().rename(
                columns={depth: 'min'}).drop(['year', 'Date'], axis=1)
            df['max'] = data.loc[locator].groupby(['day', 'month'], as_index=False).max().rename(
                columns={depth: 'max'}).drop(['year', 'Date'], axis=1)['max']
        df.sort_values(['month', 'day'], inplace=True)
        df['date'] = pd.to_datetime(
            '2020/' + df["month"].astype(int).astype(str) + "/" + df["day"].astype(int).astype(str))
        df.set_index('date', inplace=True)
        df.drop(['month', 'day'], axis=1, inplace=True)

        return df

    def __spike_plot_setter(self, data, prop, target_year, depth, percentile_legend, this_year_legend):
        # Starts the axes and plots the data for the spikes plot
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
            ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01',
             '12-01'])
        plt.xlim((data.index[0], data.index[-1]))
        ax.set_xticklabels(prop.unique())

        plt.ylim(12, self.max_temperature)
        plt.yticks(np.arange(12, self.max_temperature + 1, 2))
        # Sets the legend in order to include the fill_between value
        fill_patch = mpatches.Patch(color='#f8e959', label='Moderate')
        spike2_patch = mpatches.Patch(color='#f66000', label='Strong')
        spike3_patch = mpatches.Patch(color='#ce2200', label='Severe')
        spike4_patch = mpatches.Patch(color='#810000', label='Extreme')
        low_patch = mpatches.Patch(color='#c7ecf2', label='Marine low spike')
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles=handles[:2] + [handles[3]] + [fill_patch, spike2_patch, spike3_patch, spike4_patch])
        plt.title(str(target_year) + ' Marine HeatWaves in ' + self.site_name + ' at ' + depth + ' meters deep')
        plt.savefig('../src/output_images/' + str(target_year) + '_spike_' + self.site_name + ' ' + depth + '.png')
        ax.remove()

    def __spike_zoom_setter(self, data, prop, target_year, depth, percentile_legend, this_year_legend):
        # Makes the plot zoomed for the summer
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
        plt.title(str(target_year) + ' Marine HeatWaves in Summer in ' + self.site_name + ' at ' + depth + ' meters deep')
        plt.savefig(
            '../src/output_images/' + str(target_year) + '_spike_Summer Months_' + self.site_name + '_' + depth + '.png')
        ax.remove()

    def __anomaly_plot_setter(self, data, prop, target_year, depth, last_years_legend, this_year_legend):
        # Starts the axes and plots the data for the anomaly plot
        ax = plt.axes()
        cycler = plt.cycler(linestyle=['-', '-', '--', '--'], color=['black', 'grey', '#01086b', '#820316'],
                            alpha=[1., 0.7, 1., 1.], linewidth=[0.7, 0.7, 0.7, 0.7])
        ax.set_prop_cycle(cycler)
        data.plot(ax=ax)

        plt.fill_between(data.index, data[last_years_legend], data[this_year_legend],
                         where=(data[this_year_legend] > data[last_years_legend]), color='#fa5a5a')
        plt.fill_between(data.index, data[last_years_legend], data[this_year_legend],
                         where=(data[this_year_legend] < data[last_years_legend]), color='#5aaaff')

        plt.xlabel('')
        plt.xticks(
            ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01',
             '12-01'])
        plt.xlim((data.index[0], data.index[-1]))
        ax.set_xticklabels(prop.unique())

        plt.title(str(target_year) + ' Anomalies in ' + self.site_name + ' at ' + depth + ' meters deep')
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles=[handles[0], handles[2], handles[3]],
                   labels=[labels[0]] + ['Historic min.', 'Historic max.'])
        plt.savefig('../src/output_images/' + str(target_year) + '_anomalies_' + self.site_name + '_' + depth + '.png')
        ax.remove()

    def __anomaly_zoom_setter(self, data, prop, target_year, depth, last_years_legend, this_year_legend):
        # Makes the plot zoomed for the summer
        prop_zoom = prop.to_list()
        prop_zoom = pd.Index(prop_zoom[prop_zoom.index('Jun'):prop_zoom.index('Oct')])
        concated_zoom = data.loc['06-01':'10-01'][:-1]
        anomaly = pd.DataFrame(concated_zoom[this_year_legend] - concated_zoom[last_years_legend],
                               index=concated_zoom.index,
                               columns=['anomaly'])
        anomaly['zero'] = 0
        ax = plt.axes()
        cycler = plt.cycler(linestyle=['-', '-', '--', '--'], color=['black', 'grey', '#01086b', '#820316'],
                            alpha=[1., 0.7, 1., 1.], linewidth=[0.7, 0.7, 0.7, 0.7])
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

        plt.title(str(target_year) + ' Anomalies in Summer in ' + self.site_name + ' at ' + depth + ' meters deep')
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles=[handles[0], handles[2], handles[3]],
                   labels=[labels[0]] + ['Historic min.', 'Historic max.'])
        plt.savefig(
            '../src/output_images/' + str(target_year) + '_anomalies_Summer Months_' + self.site_name + '_' + depth + '.png')
        ax.remove()

    def marine_heat_spikes_plotter(self, data, depth, target_year):
        """
        Calculates and plots the heat spikes of a given depth for a given year

        Parameters
        ----------
        data : DataFrame
            DataFrame containing all the temperature data to be plotted

        depth : str
            Depth for which the heat spike will be calculated

        target_year : int
            Year for which the heat spike wants to be calculated and plotted
        """
        data, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend = self.__marine_heat_spikes_setter(
            data, target_year)
        last_years_filtered = self.__marine_heat_spikes_filter(data, depth)
        last_years_means = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year)
        last_years_percentile = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, percentile_legend,
                                                                  target_year, type='percentile', percentile=.9)
        this_year_mean = self.__marine_heat_spikes_df_setter(data, depth, this_year_legend, target_year, years='new')
        low_percentile = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, low_percentile_legend,
                                                           target_year, type='percentile', percentile=.1)
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
        self.__spike_plot_setter(concated, prop, target_year, depth, percentile_legend, this_year_legend)
        self.__spike_zoom_setter(concated, prop, target_year, depth, percentile_legend, this_year_legend)

    def anomalies_plotter(self, data, depth, target_year):
        """
        Calculates and plots the anomaly of a given depth for a given year

        Parameters
        ----------
        data : DataFrame
            DataFrame containing all the temperature data to be plotted

        depth : str
            Depth for which the anomaly will be calculated

        target_year : int
            Year for which the anomaly wants to be calculated and plotted
        """
        data, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend = self.__marine_heat_spikes_setter(
            data, target_year, clim=True)
        last_years_filtered = self.__marine_heat_spikes_filter(data, depth)
        last_years_means = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year)
        this_year_mean = self.__marine_heat_spikes_df_setter(data, depth, this_year_legend, target_year, years='new')
        min_max_temp = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year,
                                                    type='minmax')
        # Sets a unique Dataframe consisting of the other three
        concated = pd.concat([last_years_means, this_year_mean, min_max_temp], axis=1)
        prop = concated.index.strftime('%b')
        concated.index = concated.index.strftime('%m-%d')
        anomaly = pd.DataFrame(concated[this_year_legend] - concated[last_years_legend], index=concated.index,
                               columns=['anomaly'])
        anomaly['zero'] = 0
        self.__anomaly_plot_setter(concated, prop, target_year, depth, last_years_legend, this_year_legend)
        self.__anomaly_zoom_setter(concated, prop, target_year, depth, last_years_legend, this_year_legend)

    def __multidepth_anomaly_plot_setter(self, data_dict, prop_dict, target_year, depths, last_years_legend,
                                       this_year_legend):
        ax = plt.axes()
        cycler = plt.cycler(linestyle=['-', '-'], color=['black', 'grey'],
                            alpha=[1., 0.7], linewidth=[0.7, 0.7])
        ax.set_prop_cycle(cycler)

        data_dict.plot(ax=ax)
        # labelLines(plt.gca().get_lines(), zorder=2.5)
        lines = ax.get_lines()
        i = 0
        for depth in depths:

            labelLine(lines[i], 200, label=depth)
            i = i + 2
        for depth in depths:
            plt.fill_between(data_dict.index, data_dict[last_years_legend[depth]], data_dict[this_year_legend[depth]],
                             where=(data_dict[this_year_legend[depth]] > data_dict[last_years_legend[depth]]),
                             color='#fa5a5a')
            plt.fill_between(data_dict.index, data_dict[last_years_legend[depth]], data_dict[this_year_legend[depth]],
                             where=(data_dict[this_year_legend[depth]] < data_dict[last_years_legend[depth]]),
                             color='#5aaaff')

        plt.xlabel('')
        plt.xticks(
            ['01-01', '02-01', '03-01', '04-01', '05-01', '06-01', '07-01', '08-01', '09-01', '10-01', '11-01',
             '12-01'])
        plt.xlim((data_dict.index[0], data_dict.index[-1]))
        ax.set_xticklabels(prop_dict.unique())

        plt.title('Anomalies in ' + self.site_name + ' in ' + str(target_year))
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles=[handles[0]], labels=['Multi-Year Mean'])
        plt.savefig('../src/output_images/' + str(target_year) + '_anomalies_' + self.site_name + '_Multidepth.png')
        ax.remove()

    def multidepth_anomaly_plotter(self, target_year, depths=['10', '25', '40']):
        """
        Calculates and plots the anomalies of multiple given depths on the same
         figure for a given year

        Parameters
        ----------
        target_year : int
            Year for which it wants to be calculated and plotted the anomalies

        depths : list of str, optional
            The depths for which the anomalies will be calculated (default=['10', '25', '40'])
        """
        data = self.df.drop(['Time'], axis=1)
        last_legend_dict = {}
        this_legend_dict = {}
        removable = []
        for depth in depths:
            if depth in data.columns:
                data_depth, last_years_legend, percentile_legend, this_year_legend, low_percentile_legend = self.__marine_heat_spikes_setter(
                    pd.DataFrame(data, columns=['Date', depth]), target_year, clim=True)
                this_year_legend = this_year_legend + ' (' + depth + 'm)'
                last_years_legend = last_years_legend + ' (' + depth + 'm)'
                last_legend_dict[depth] = last_years_legend
                this_legend_dict[depth] = this_year_legend
                last_years_filtered = self.__marine_heat_spikes_filter(data_depth, depth)
                last_years_means = self.__marine_heat_spikes_df_setter(last_years_filtered, depth, last_years_legend, target_year)
                this_year_mean = self.__marine_heat_spikes_df_setter(data_depth, depth, this_year_legend, target_year, years='new')

                # Sets a unique Dataframe consisting of the other three

                if depths.index(depth) == 0:
                    concated = pd.concat([last_years_means, this_year_mean], axis=1)
                    prop = concated.index.strftime('%b')
                else:
                    concated = pd.concat([concated, last_years_means, this_year_mean], axis=1)
            else:
                removable.append(depth)
        for depth in removable:
            depths.remove(depth)

        concated.index = concated.index.strftime('%m-%d')

        self.__multidepth_anomaly_plot_setter(concated, prop, target_year, depths, last_legend_dict,
                                       this_legend_dict)

    def browse_heat_spikes(self, year):
        """
        Erases the Time column on the df attribute to use it later to calculate and
        plot the heat spikes of a given year in all its depths

        Parameters
        ----------
        year : int
            Year for which it wants to be calculated and plotted the heat spikes
        """
        data = self.df.drop(['Time'], axis=1)
        for depth in data.columns[1:]:
            self.marine_heat_spikes_plotter(pd.DataFrame(data, columns=['Date', depth]), depth, year)

    def browse_anomalies(self, year):
        """
        Erases the Time column on the df attribute to use it later to calculate and
        plot the anomalies of a given year in all its depths

        Parameters
        ----------
        year : int
            Year for which it wants to be calculated and plotted the anomalies
        """
        data = self.df.drop(['Time'], axis=1)
        for depth in data.columns[1:]:
            self.anomalies_plotter(pd.DataFrame(data, columns=['Date', depth]), depth, year)

