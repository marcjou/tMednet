import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.colors as mcol
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patches as ptch
from matplotlib.colors import ListedColormap, BoundaryNorm
import time
import seaborn as sns
import math
import imageio
import logging
import calendar
import numpy as np
import xarray as xr
import pandas as pd
from sys import _getframe
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from typing import Literal, get_args, get_origin
from shapely.validation import make_valid
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class MME_Plot:

    def __init__(self, PATH):
        self.df_events = pd.read_excel('../src/MME.xlsx', sheet_name='Quim Years with MME')
        self.df_numbers = pd.read_excel('../src/MME.xlsx', sheet_name='Massimo original dataset')
        self.df_fishes = pd.read_excel('../src/Example_Visual_census_ALL.xlsx', 'DATA-All')
        self.df_corals = pd.read_excel('../src/AtencioCoralls_ProjecteCORFUN.xlsx', 'Censos Drive')
        df_coords = pd.read_excel('../src/Coords.xlsx')
        self.df_map = pd.merge(self.df_events, df_coords[['id.hexagon', 'Lat', 'Lon']], on='id.hexagon', how='left')
        self.df_events.columns = self.df_events.columns.astype(str)
        self.columns = self.df_events.columns[4:]
        self.coords = pd.read_csv('../src/Ecoregion coords.csv')

    def plot_return_time_regional(self, reg):
        plt.clf()
        df_scatter = self.create_scatter_dataframe()
        df_reg = df_scatter.loc[df_scatter['sub-ecoregion'] == reg]
        df = self.create_dict_df(df_reg)
        df_sorted_yearly = self.create_dataframe_sorted(df)
        min_size = np.min(df_sorted_yearly['Count']) * 10
        max_size = np.max(df_sorted_yearly['Count']) * 10
        ax_scatter_years2 = sns.scatterplot(df_sorted_yearly, x='Year', y='Return tax', size='Count', sizes=(min_size, max_size),
                                            alpha=.5, legend='brief')
        ax_scatter_years2 = sns.lineplot(df_sorted_yearly, x='Year', y='Max Return', color='k')
        ax_scatter_years2 = sns.regplot(df_sorted_yearly, x='Year', y='Mean', ci=None, color='tab:orange')
        leg = plt.legend(loc='upper right', labels=['Max return years', 'Regression', 'Nº of Events'])
        ax_scatter_years2.add_artist(leg)
        plt.legend(loc=[0.8, 0.3])
        plt.title(reg)
        ax_scatter_years2.set(ylabel='Return Years')
        plt.savefig('../src/output_images/Returning Time_' + reg + '.png',
                    bbox_inches='tight')
        print('ha')

    def create_scatter_dataframe(self):
        df_return = self.df_events.copy()
        ret_counter = 0
        old_year = ''
        for idx, row in self.df_events.iterrows():
            for year in self.columns:
                if row[year] == 1 or year == self.columns[-1]:
                    if year == '2020':
                        print('ye')
                    ret_counter = ret_counter + 1
                    if old_year == '':
                        old_year = year
                        if year == self.columns[-1]:
                            old_year = ''
                            ret_counter = 0
                            df_return[year][idx] = np.nan
                    else:
                        if year == self.columns[-1]:
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

        return df_scatter

    def create_dict_df(self, df_scatter):
        dict_for_yearly = {'Year': '', 'Return years': 0, 'Count': 0}

        dict_list_yearly = []
        for i in range(1, 41):
            for year in df_scatter['Year'].unique():
                dict_for_yearly['Year'] = year
                dict_for_yearly['Return years'] = i
                dict_for_yearly['Count'] = df_scatter['Return time'].loc[
                    (df_scatter['Year'] == year) & (df_scatter['Return time'] == i)].count()
                dict_list_yearly.append(dict_for_yearly.copy())

        df = pd.DataFrame.from_records(dict_list_yearly)

        return df

    def create_dataframe_sorted(self, df):
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
            df_sorted_yearly.loc[df_sorted_yearly['Return tax'] > 0].groupby(df_sorted_yearly['Year'])[
                'Count'].transform('sum'), 2)
        return df_sorted_yearly

    def plot_return_time(self):
        plt.clf()
        df_scatter = self.create_scatter_dataframe()
        df = self.create_dict_df(df_scatter)
        df_sorted_yearly = self.create_dataframe_sorted(df)
        min_size = np.min(df_sorted_yearly['Count']) * 10
        max_size = np.max(df_sorted_yearly['Count']) * 10
        ax_scatter_years = sns.scatterplot(df_sorted_yearly, x='Year', y='Return tax', size='Count', sizes=(min_size, max_size),
                                           alpha=.5, legend='brief')
        ax_scatter_years = sns.lineplot(df_sorted_yearly, x='Year', y='Max Return', color='k')
        ax_scatter_years = sns.regplot(df_sorted_yearly, x='Year', y='Mean', color='tab:orange')
        leg = plt.legend(loc='upper right', labels=['Max return years', 'Regression', 'Nº of Events'])
        ax_scatter_years.add_artist(leg)
        plt.legend(loc=[0.8, 0.5])
        ax_scatter_years.set(ylabel='Return Years')
        from matplotlib.ticker import AutoMinorLocator, MultipleLocator
        ax_scatter_years.set_xlim([1978.5, 2020.5])
        ax_scatter_years.xaxis.set_major_locator(MultipleLocator(5))
        ax_scatter_years.xaxis.set_minor_locator(MultipleLocator(1))
        self.save_image('Returning Time_Mediterranean')
        
    def plot_map_regional(self, reg):
        # Use only the pixels with more than a year of mortality
        self.df_map = self.df_map.loc[self.df_map['#Years with MME'] > 1]
        df = self.df_map.loc[self.df_map['sub-ecoregion'] == reg]
        if (reg == 'Southwestern Mediterranean') or (reg == 'Northwestern Mediterranean'):
            reg_df = self.coords.loc[self.coords['ECOREGION'] == 'Western Mediterranean']
        else:
            reg_df = self.coords.loc[self.coords['ECOREGION'] == reg]
        print('Before setting axes for ' + reg)
        ax, gl = self.ax_setter(float(reg_df['Lat1']), float(reg_df['Lat2']), float(reg_df['Lon1']), float(reg_df['Lon2']))
        print('Axes set')
        cmap = 'autumn_r'
        nyears = ax.scatter(x=df['Lon'], y=df['Lat'], c=df['#Years with MME'],
                            transform=ccrs.PlateCarree(), cmap=cmap, alpha=0.7, s=15, edgecolor='blue', linewidths=0.5)
        cb = plt.colorbar(nyears, ticks=range(0, 41), label='No of Years with MME')
        print('Plotted, time to save')
        plt.title(reg)
        self.save_image('Years per pixel_' + reg)

    def regional_returntime_composer(self):
        self.loop_ecoregion(self.plot_return_time_regional)
    def regional_map_composer(self):
        self.loop_ecoregion(self.plot_map_regional)
    def plot_data_map(self):
        '''plt.clf()
        # Use only the pixels with more than a year of mortality
        self.df_map = self.df_map.loc[self.df_map['#Years with MME'] > 1]
        ax, gl = self.ax_setter()
        cmap = 'autumn_r'
        nyears = ax.scatter(x=self.df_map['Lon'], y=self.df_map['Lat'], c=self.df_map['#Years with MME'],
                            transform=ccrs.PlateCarree(), cmap=cmap, alpha=0.7, s=15, edgecolor='blue', linewidths=0.5)
        cb = plt.colorbar(nyears, ticks=range(0, 41), label='No of Years with MME')'''
        plt.clf()
        cmap = 'autumn_r'
        #self.df_map['Record range'] = (self.df_map['#Records MMEs_All_years_']/10).apply(np.floor)*10
        #Set the categories
        self.df_map['Record range'] = self.df_map['#Records MMEs_All_years_'].apply(
            lambda y: 0.2 if y < 10 else (0.4 if y < 50 else (0.6 if y < 100 else (0.8 if y < 200 else 1))))
        self.df_map['Log10 Records'] = np.log10(self.df_map['#Records MMEs_All_years_'])
        ax, gl = self.ax_setter()
        nyears = ax.scatter(x=self.df_map['Lon'], y=self.df_map['Lat'], c=self.df_map['Log10 Records'],
                            transform=ccrs.PlateCarree(), alpha=1, s=15, edgecolor='blue', linewidths=0.5, cmap=cmap)
        cb = plt.colorbar(nyears, label='No of Records across all years')
        cb.set_ticks([np.log10(1), np.log10(10), np.log10(50), np.log10(100), np.log10(200)])
        cb.set_ticklabels(['1-10', '10-50', '50-100', '100-200', '>200'])
        self.save_image('Records across years Map')
    def plot_affected_percentage(self):
        y_axis = self.df_events['#Years with MME'].unique()
        y_axis.sort()
        total_hex = self.df_events['#Years with MME'].count()
        df_inc = pd.DataFrame([self.df_events['#Years with MME'].loc[self.df_events['#Years with MME'] == i].count() for i in y_axis],
                              columns=['count'])
        df_inc['% affected'] = (df_inc['count'] / total_hex) * 100
        df_inc['N affected'] = df_inc['count']
        df_inc['y_axis'] = y_axis
        ax = df_inc.plot.bar(x='y_axis', y='% affected')
        ax.set_xlabel('Years with MME')
        ax.set_ylabel('Percentage of affected hexagons')
        ax.set_ylim([0, 70])
        plt.xticks(rotation=0)
        ax.get_legend().remove()
        plt.title('Mediterranean MME')
        self.save_image('MME_Global')

    def plot_affected_number(self):
        df_third = self.get_numbered_df()
        df_third['Year'] = df_third['Year'].astype(int)
        ax = df_third.plot.bar(x='Year', y='Count', figsize=(10, 5))
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of affected hexagons')
        ax.set_ylim([0, df_third['Count'].max() + 25])
        plt.xticks(rotation=90)
        ax.get_legend().remove()
        plt.title('Mediterranean MME')
        self.save_image('MME_N_Global')

    def get_numbered_df(self):
        df_third = pd.DataFrame(self.columns, columns=['Year'])
        df_third['Count'] = 0
        for year in self.columns:
            df_third['Count'].loc[df_third['Year'] == year] = self.df_events[year].sum()
        return df_third

    def save_image(self, title):
        plt.savefig('../src/output_images/' + title + '.png',
                    bbox_inches='tight')

    def affected_percentage_regional_composer(self):
        self.loop_ecoregion(self.plot_affected_percentage_regional)

    def affected_numbers_regional_composer(self):
        self.loop_ecoregion(self.plot_affected_numbers_regional)

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

    def plot_affected_numbers_regional(self, reg):
        df_third = self.get_numbered_df()
        total_max = df_third['Count'].max()
        for year in self.columns:
            df_third['Count'].loc[df_third['Year'] == year] = self.df_events[year].loc[self.df_events['sub-ecoregion'] == reg].sum()
        ax = df_third.plot.bar(x='Year', y='Count', figsize=(10, 5))
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of affected hexagons')
        ax.set_ylim([0, total_max + 25])
        plt.xticks(rotation=90)
        ax.get_legend().remove()
        plt.title(reg + ' MME')
        self.save_image('MME_N_' + reg)

    def setup_heatmap_base(self):
        events_copy = self.df_events.copy()
        events_copy.replace(0, np.nan, inplace=True)
        events_copy.index = events_copy['sub-ecoregion']
        for i in self.df_events.columns[:4]:
            del events_copy[i]
        myColors = ((1.0, 1.0, 1.0, 1.0), (0.8, 0.0, 0.0, 1.0))
        cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
        return events_copy, cmap

    def plot_heatmap_base(self):
        plt.clf()
        events_copy, cmap = self.setup_heatmap_base()
        reg = events_copy.index.unique()
        yticks = []
        for i in reg:
            yticks.append(events_copy.index.get_indexer_for((events_copy[events_copy.index == i].index))[0])
        num_ticks = len(reg)
        reg_list = events_copy.index
        # the content of labels of these yticks
        yticklabels = [reg_list[idx] for idx in yticks]

        ax = sns.heatmap(events_copy, cmap=cmap, yticklabels=yticklabels, vmax=1, vmin=0, cbar_kws={'ticks': [0, 1]})
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        self.save_image('Heatmap Global')

    def plot_heatmap_base_regional(self, reg):
        events_copy, cmap = self.setup_heatmap_base()
        plt.clf()
        ax = sns.heatmap(events_copy.loc[events_copy.index == reg], cmap=cmap, yticklabels=False, vmax=1, vmin=0,
                         cbar_kws={'ticks': [0, 1]})
        ax.set_ylabel(reg)
        self.save_image('Heatmap ' + reg)

    def heatmap_base_composer(self):
        self.loop_ecoregion(self.plot_heatmap_base_regional)

    def plot_fish_assesment(self):
        plt.clf()
        ax, gl = self.ax_setter()
        cmap = self.fish_assesment()
        asses = ax.scatter(x=self.df_fishes['LONG'], y=self.df_fishes['LAT'], c=self.df_fishes['Assesment'],
                           transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                           vmax=3, zorder=10)
        cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
        cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
        self.save_image('Fish Assesment')

    def plot_fish_assesment_zoom(self):
        plt.clf()
        ax, gl = self.ax_setter(lat1=-5.49, lat2=21.60, lon1=35.82, lon2=45.86)
        cmap = self.fish_assesment()
        asses = ax.scatter(x=self.df_fishes['LONG'], y=self.df_fishes['LAT'], c=self.df_fishes['Assesment'],
                           transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                           vmax=3, zorder=10)
        cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
        cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
        self.save_image('Fish Assesment_Zoom')

    def fish_assesment(self):
        self.df_fishes['Assesment'] = self.df_fishes['Tropical. Index'].apply(
            lambda y: 0 if y <= 1 else (1 if y <= 3 else (2 if y <= 5 else 3)))
        colors = ['green', 'yellow', 'orange', 'red']
        cmap = LinearSegmentedColormap.from_list('Custom', colors, len(colors))
        return cmap

    def plot_yearly_fish_assesment(self):
        for year in self.df_fishes['YEAR'].unique():
            plt.clf()
            ax, gl = self.ax_setter()
            cmap = self.fish_assesment()
            df = self.df_fishes.loc[self.df_fishes['YEAR'] == year]
            asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment'],
                               transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                               vmax=3, zorder=10)
            cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
            cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
            plt.title('Fish census ' + str(year))
            self.save_image('Fish Assesment ' + str(year))

    def plot_yearly_fish_assesment_zoom(self):
        for year in self.df_fishes['YEAR'].unique():
            plt.clf()
            ax, gl = self.ax_setter(lat1=-5.49, lat2=21.60, lon1=35.82, lon2=45.86)
            cmap = self.fish_assesment()
            df = self.df_fishes.loc[self.df_fishes['YEAR'] == year]
            asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment'],
                               transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                               vmax=3, zorder=10)
            cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
            cb.set_ticklabels(['Tempered', 'Warm', 'Tropicalized', 'Highly Tropicalized'])
            plt.title('Fish census ' + str(year))
            self.save_image('Fish Assesment Zoom ' + str(year))

    def plot_mortality_assesment(self):
        ax, gl = self.ax_setter()
        cmap = self.mortality_assesment()
        asses = ax.scatter(x=self.df_corals['LONG'], y=self.df_corals['LAT'], c=self.df_corals['Assesment'],
                           transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                           vmax=3, zorder=10)
        cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
        cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])
        self.save_image('Mortality Assesment')

    def plot_mortality_assesment_zoom(self, type='All', coords = [3.00, 3.43, 41.74, 42.42], place='', specie='All'):
        ax, gl = self.ax_setter(lat1=coords[0], lat2=coords[1], lon1=coords[2], lon2=coords[3])
        cmap = self.mortality_assesment(type)
        if specie != 'All':
            self.df_corals = self.df_corals.loc[self.df_corals['Species'] == specie].sort_values('Size', ascending=False)
        else:
            self.df_corals = self.df_corals.sort_values('Size', ascending=False)
        asses = ax.scatter(x=self.df_corals['LONG'], y=self.df_corals['LAT'], c=self.df_corals['Assesment'],
                           transform=ccrs.PlateCarree(), s=self.df_corals['Size']*5, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                           vmax=3, zorder=10, alpha=0.7)
        cb = plt.colorbar(asses, ticks=range(0, 5), shrink=0.5, label='Assesment')
        cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])
        plt.title('Mortality assesment ' + type + ' ' + specie)
        self.save_image('Mortality Assesment Zoom ' + type + ' ' + place + ' ' + specie)

    def mortality_assesment(self, type='All'):
        indx = self.df_corals.loc[self.df_corals['Total colonies'] == 0].index
        self.df_corals.drop(index=indx, inplace=True)
        if type == 'All':
            self.df_corals['Assesment'] = self.df_corals['% Affected all'].apply(
                lambda y: 0 if y <= 10 else (1 if y <= 30 else (2 if y < 60 else 3)))
        elif type == 'Old':
            self.df_corals['Assesment'] = self.df_corals['% Affected old'].apply(
                lambda y: 0 if y <= 10 else (1 if y <= 30 else (2 if y < 60 else 3)))
        elif type == 'Recent':
            self.df_corals['Assesment'] = self.df_corals['% Affected recent'].apply(
                lambda y: 0 if y <= 10 else (1 if y <= 30 else (2 if y < 60 else 3)))
        colors = ['green', 'yellow', 'orange', 'red']
        cmap = LinearSegmentedColormap.from_list('Custom', colors, len(colors))
        df_sizes = self.df_corals.pivot_table(index=['LAT', 'LONG'], aggfunc='size')
        df_sizes = df_sizes.reset_index()
        df_sizes = df_sizes.rename(columns={0: 'Size'})
        for i in range(0, len(df_sizes)):
            self.df_corals.loc[(self.df_corals['LAT'] == df_sizes['LAT'][i]) & (self.df_corals['LONG'] == df_sizes['LONG'][i]), 'Size'] = df_sizes['Size'][i]
        return cmap

    def plot_yearly_mortality_assesment(self):
        for year in self.df_corals['YEAR'].unique():
            plt.clf()
            ax, gl = self.ax_setter()
            cmap = self.mortality_assesment()
            df = self.df_corals.loc[self.df_corals['Year'] == year]
            asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment'],
                               transform=ccrs.PlateCarree(), s=20, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                               vmax=3, zorder=10)
            cb = plt.colorbar(asses, ticks=range(0, 5), label='Assesment')
            cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])
            plt.title('Mortality Assesment ' + str(year))
            self.save_image('Mortality Assesment ' + str(year))

    def generate_all_histogram(self, species='All', type='All', place=''):
        for year in self.df_corals['Year'].unique():
            plt.clf()
            cmap = self.mortality_assesment(type)
            if species == 'All':
                df = self.df_corals.loc[self.df_corals['Year'] == year]
            else:
                df = self.df_corals.loc[
                    (self.df_corals['Year'] == year) & (self.df_corals['Species'] == species) & (self.df_corals['Main site'] == place)]
            if type == 'All':
                affected = '% Affected all'
            elif type == 'Old':
                affected = '% Affected old'
            elif type == 'Recent':
                affected = '% Affected recent'

            df_histo = df[affected].sort_values(ascending=False).reset_index()
            self.create_histogram(df_histo, affected, 'Histogram ' + affected + ' ' + species + ' ' + place, show_title=False)

    def plot_yearly_mortality_assesment_zoom(self, species='All', type='All', coords=[3.00, 3.43, 41.74, 42.42], place=''):
        for year in self.df_corals['Year'].unique():
            plt.clf()
            category_colors = ['#3faa59','#fbfcd0', '#ffcf3d', '#ff6a6c']
            ax, gl, fig = self.ax_setter(lat1=coords[0], lat2=coords[1], lon1=coords[2], lon2=coords[3], subplot=True)
            # ax, gl, fig = self.ax_setter(lat1=-5.49, lat2=21.60, lon1=35.82, lon2=45.86, subplot=True)
            cmap = self.mortality_assesment(type)
            if species == 'All':
                df = self.df_corals.loc[self.df_corals['Year'] == year]
            else:
                df = self.df_corals.loc[
                    (self.df_corals['Year'] == year) & (self.df_corals['Species'] == species) & (self.df_corals['Main site'] == place)]
            if type == 'All':
                affected = '% Affected all'
            elif type == 'Old':
                affected = '% Affected old'
            elif type == 'Recent':
                affected = '% Affected recent'

            df_histo = df[affected].sort_values(ascending=False).reset_index()
            my_cmap = matplotlib.colors.ListedColormap(category_colors, name='my_colormap_name')

            asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment'],
                               transform=ccrs.PlateCarree(), s=20, cmap=my_cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                               vmax=3, zorder=10, alpha=0.7)
            cb = plt.colorbar(asses, ticks=range(0, 5), shrink=0.5, label='Assesment')
            cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])
            plt.title('Mortality Assesment ' + str(year) + ' ' + species + ' ' + type)


            # Bar plot
            mask_no = df_histo[affected] < 10
            mask_lo = (df_histo[affected] >= 10) & (df_histo[affected] < 30)
            mask_mod = (df_histo[affected] >= 30) & (df_histo[affected] < 60)
            mask_hi = (df_histo[affected] >= 60)

            category = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']
            df_total_hist = pd.DataFrame()
            df_total_hist['Cat'] = category
            df_total_hist['Count'] = [len(df_histo[mask_no])/len(df_histo), len(df_histo[mask_lo])/len(df_histo), len(df_histo[mask_mod])/len(df_histo), len(df_histo[mask_hi])/len(df_histo)]
            '''fig, ax3 = plt.subplots()
            ax3.set_facecolor('#97b6e1')

            ax3.bar(0, df_total_hist['Count'][0], color=category_colors[0])
            ax3.bar(1, df_total_hist['Count'][1], color=category_colors[1])
            ax3.bar(2, df_total_hist['Count'][2], color=category_colors[2])
            ax3.bar(3, df_total_hist['Count'][3], color=category_colors[3])'''

            ax2 = fig.add_subplot(2,1,2)
            ax2.set_facecolor('#97b6e1') # Light Grey #e6e6e6, Ligth Blue #8a87de
            ax2.bar(df_histo.index[mask_no], df_histo[affected][mask_no], color=category_colors[0], align='edge', width=1)
            ax2.bar(df_histo.index[mask_lo], df_histo[affected][mask_lo], color=category_colors[1], align='edge', width=1)
            ax2.bar(df_histo.index[mask_mod], df_histo[affected][mask_mod], color=category_colors[2], align='edge', width=1)
            ax2.bar(df_histo.index[mask_hi], df_histo[affected][mask_hi], color=category_colors[3], align='edge', width=1)
            #ax2.bar(df_histo.index, df_histo['% Affected all'])
            ax2.set_xticks([])
            ax2.set_ylim([0, 100])
            ax2.set_ylabel(affected)
            ax2.axhline(y = 10, color = category_colors[0], linestyle = '-')
            ax2.axhline(y=30, color=category_colors[1], linestyle='-')
            ax2.axhline(y=60, color=category_colors[2], linestyle='-')
            # Percentage mortality
            '''
            ax2.add_patch(plt.Rectangle((-1,0), len(df_histo.index) + 1, 10, facecolor=category_colors[0], zorder=0))
            ax2.add_patch(plt.Rectangle((-1, 10), len(df_histo.index) + 1, 20, facecolor=category_colors[1], zorder=0))
            ax2.add_patch(plt.Rectangle((-1, 30), len(df_histo.index) + 1, 30, facecolor=category_colors[2], zorder=0))
            ax2.add_patch(plt.Rectangle((-1, 60), len(df_histo.index) + 1, 40, facecolor=category_colors[3], zorder=0))
            '''
            extent = ax2.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            print('Year ' + str(year) + ' Plotter')
            if species == 'All':
                self.save_image('Mortality Assesment Zoom + Histogram ' + str(int(year)) + ' ' + type)
                fig.savefig('../src/output_images/Histogram ' + str(int(year)) + ' ' + type + '.png', bbox_inches=extent.expanded(1.15, 1.2))
            else:
                self.save_image('Mortality Assesment Zoom + Histogram ' + str(int(year)) + '__' + str(species) + ' ' + type + ' ' + place)
                fig.savefig('../src/output_images/Histogram ' + str(int(year)) + '__' + str(species) + ' ' + type + ' ' + place +'.png', bbox_inches=extent.expanded(1.15, 1.2))

    def census_horizontal_assesment_total(self, dfin, kind, site='', ass='All', specie='All'):
        if specie!= 'All' and site!='':
            df = dfin.loc[(dfin['species'] == specie) & (dfin['Main site'] == site)].copy()
        elif specie!= 'All':
            df = dfin.loc[(dfin['species'] == specie)].copy()
        else:
            df = dfin.copy()
        df['Depth range'] = df['depth'].apply(
            lambda y: '05-10' if y <= 10 else ('10-15' if y <= 15 else ('15-20' if y <= 20 else '20-25' if y <= 25 else '25-30' if y <= 30 else '30-35')))
        # Assesment tip: 0 means No, 1 Low, 2 Moderate, 3 Severe
        df_assesment_depthly = df.groupby('Depth range')['Assesment ' + ass].value_counts(normalize=True).unstack(
            'Assesment ' + ass).fillna(0).sort_values('Depth range')
        # Check if the columns correspond to all the assesment categories, if not, add them
        ass_columns = [0, 1, 2, 3]
        if list(df_assesment_depthly.columns) != ass_columns:
            for i in ass_columns:
                if i not in list(df_assesment_depthly.columns):
                    df_assesment_depthly[i] = 0.0
            df_assesment_depthly = df_assesment_depthly[ass_columns]
        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        category_colors = ['#3faa59', '#fbfcd0', '#ffcf3d', '#ff6a6c']
        df = df_assesment_depthly.iloc[::-1]
        df = df[df.columns[::-1]]
        if df.empty:
            return
        df.plot.barh(ax=ax, stacked=True, color=category_colors[::-1])
        category_names = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

        ax.legend(ncol=len(category_names), labels=category_names[::-1], bbox_to_anchor=(0, 1),
                  loc='lower left', fontsize='small')
        self.save_image('Horizontal Assesment total ' + kind + ' ' + ass + ' ' + specie + ' ' + site)

    def horizontal_mortality_percentage(self, type='year', site='', ass='All', specie='All'):

        cmap = self.mortality_assesment(ass)
        if specie!= 'All':
            df = self.df_corals.loc[(self.df_corals['Species'] == specie) & (self.df_corals['Main site'] == site)].copy()
        else:
            df = self.df_corals.copy()
        if type == 'year':
            #Assesment tip: 0 means No, 1 Low, 2 Moderate, 3 Severe
            df_assesment_yearly = df.groupby('Year')['Assesment'].value_counts(normalize=True).unstack(
                'Assesment').fillna(0).sort_values('Year')


            fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
            ax = fig.add_subplot(1,1,1)
            category_colors = ['#3faa59','#fbfcd0', '#ffcf3d', '#ff6a6c']

            df_assesment_yearly.plot.barh(ax=ax, stacked=True, color=category_colors)
            category_names = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

            ax.legend(ncol=len(category_names), labels=category_names, bbox_to_anchor=(0, 1),
                      loc='lower left', fontsize='small')
        else:
            # Assesment tip: 0 means No, 1 Low, 2 Moderate, 3 Severe
            df_assesment_depthly = df.groupby('Depth range')['Assesment'].value_counts(normalize=True).unstack(
                'Assesment').fillna(0).sort_values('Depth range')

            fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
            ax = fig.add_subplot(1, 1, 1)
            category_colors = ['#3faa59', '#fbfcd0', '#ffcf3d', '#ff6a6c']
            df = df_assesment_depthly.iloc[::-1]
            df = df[df.columns[::-1]]
            df.plot.barh(ax=ax, stacked=True, color=category_colors[::-1])
            category_names = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

            ax.legend(ncol=len(category_names), labels=category_names[::-1], bbox_to_anchor=(0, 1),
                      loc='lower left', fontsize='small')
        self.save_image('Horizontal Assesment total ' + ass + ' ' + specie + ' ' + site)


    def census_horizontal_mortality(self, df, kind, affected, type, specie='All', site=''):
        plt.clf()
        category_colors = ['#3faa59', '#fbfcd0', '#ffcf3d', '#ff6a6c']
        fig = plt.figure(figsize=(20 / 2.54, 7 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        if specie != 'All' and site != '':
            df = df.loc[(df['species'] == specie) & (
                        df['Main site'] == site)]
        elif specie != 'All':
            df = df.loc[(df['species'] == specie)]
        if df.empty:
            return
        else:
            # Horizontal bar
            if site != '':
                df_assesment_yearly = df.groupby('Main site')['Assesment ' + affected].value_counts(normalize=True).unstack(
                    'Assesment ' + affected).fillna(0)
            else:
                df_assesment_yearly = df['Assesment ' + affected].value_counts(normalize=True).to_frame().T
            # Check if the columns correspond to all the assesment categories, if not, add them
            ass_columns = [0, 1, 2, 3]
            if list(df_assesment_yearly.columns) != ass_columns:
                for i in ass_columns:
                    if i not in list(df_assesment_yearly.columns):
                        df_assesment_yearly[i] = 0.0
                df_assesment_yearly = df_assesment_yearly[ass_columns]
            # Invert columns to show first the highest mortality
            df_assesment_yearly = df_assesment_yearly.iloc[:, ::-1]
            df_assesment_yearly.plot.barh(ax=ax, stacked=True, color=category_colors[::-1])
            category_names = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

            ax.legend(ncol=len(category_names), labels=category_names[::-1], bbox_to_anchor=(0, 1),
                      loc='lower left', fontsize='small')
            self.save_image('Horizontal Assesment ' + kind + ' ' + str(type) + '  ' + str(specie) + ' ' + str(site))
    def yearly_horizontal_mortality_percentage(self, specie='All', site='', type='All'):
        for year in self.df_corals['Year'].unique():
            try:
                plt.clf()
                category_colors = ['#3faa59','#fbfcd0', '#ffcf3d', '#ff6a6c']
                fig = plt.figure(figsize=(20 / 2.54, 7 / 2.54))
                ax = fig.add_subplot(1, 1, 1)
                cmap = self.mortality_assesment(type)
                if specie != 'All':
                    df = self.df_corals.loc[(self.df_corals['Year'] == year) & (self.df_corals['Species'] == specie) & (self.df_corals['Main site'] == site)]
                else:
                    df = self.df_corals.loc[(self.df_corals['Year'] == year)]
                # Horizontal bar
                df_assesment_yearly = df.groupby('Year')['Assesment'].value_counts(normalize=True).unstack(
                    'Assesment').fillna(0).sort_values('Year')
                # Check if the columns correspond to all the assesment categories, if not, add them
                ass_columns = [0,1,2,3]
                if list(df_assesment_yearly.columns) != ass_columns:
                    for i in ass_columns:
                        if i not in list(df_assesment_yearly.columns):
                            df_assesment_yearly[i] = 0.0
                    df_assesment_yearly = df_assesment_yearly[ass_columns]
                # Invert columns to show first the highest mortality
                df_assesment_yearly = df_assesment_yearly.iloc[:, ::-1]
                df_assesment_yearly.plot.barh(ax=ax, stacked=True, color=category_colors[::-1])
                category_names = ['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact']

                ax.legend(ncol=len(category_names), labels=category_names[::-1], bbox_to_anchor=(0, 1),
                          loc='lower left', fontsize='small')
                self.save_image('Horizontal Assesment ' +str(type) + ' ' + str(year) + ' ' + str(specie) + ' ' + str(site))
            except:
                print('No numeric data to plot for ' + str(year))

    def mortality_by_species(self):
        species = self.df_corals['Species'].dropna().unique()
        for specie in species:
            self.plot_yearly_mortality_assesment_zoom(species=specie)

    def create_full_census_plots(self):
        df_census = pd.read_excel('../src/AtencioCoralls_CensusPopulation.xlsx', 'Census')
        df_pop_all = pd.read_excel('../src/AtencioCoralls_CensusPopulation.xlsx', 'Population % Affected all')
        df_pop_rec = pd.read_excel('../src/AtencioCoralls_CensusPopulation.xlsx', 'Population % Affected recent')

        df_census, cmap_census = self.mortality_assesment_modified(df_census, ['% Affected all', '% Affected recent'])
        df_pop_all, bad = self.mortality_assesment_modified(df_pop_all, ['% Affected all'])
        df_pop_rec, bad = self.mortality_assesment_modified(df_pop_rec, ['% Affected recent'])
        site_dict = {'Cap de creus' : [3.09, 3.38, 42.21, 42.42], 'Palamos' : [2.85, 3.49, 41.72, 42.12] }
        for specie in df_census['species'].unique():
            for key in site_dict:
                for aff in ['% Affected all', '% Affected recent']:
                    if aff == '% Affected all':
                        typer = 'All'
                    else:
                        typer = 'Recent'
                    self.plot_mortality_assesment_zoom_modified(df_census, cmap_census, 'census', aff, type=typer, specie=specie, coords=site_dict[key], place=key)
                    self.census_horizontal_mortality(df_census, 'census', aff, typer, specie=specie, site=key)
                    self.create_histogram(df_census, aff, 'Hisogram census ' + typer + ' ' + specie + ' ' + key, site=key, species=specie, show_title=False)
                    self.census_horizontal_assesment_total(df_census, 'census', site=key, ass=aff, specie=specie)
                self.plot_mortality_assesment_zoom_modified(df_pop_all, cmap_census, 'population', '% Affected all', type='All',
                                                            specie=specie, coords=site_dict[key],
                                                            place=key)
                self.census_horizontal_mortality(df_pop_all, 'population', '% Affected all', type='All', specie=specie, site=key)
                self.create_histogram(df_pop_all, '% Affected all', 'Histogram population All ' + ' ' + specie + ' ' + key, site=key,
                                      species=specie, show_title=False, errbar=True)
                self.census_horizontal_assesment_total(df_pop_all, 'population', site=key, ass='% Affected all', specie=specie)
                self.plot_mortality_assesment_zoom_modified(df_pop_rec, cmap_census, 'population', '% Affected recent', type='Recent',
                                                            specie=specie, coords=site_dict[key],
                                                            place=key)
                self.census_horizontal_mortality(df_pop_rec, 'population', '% Affected recent', type='Recent', specie=specie,
                                                 site=key)
                self.create_histogram(df_pop_rec, '% Affected recent',
                                      'Histogram population Recent ' + ' ' + specie + ' ' + key, site=key,
                                      species=specie, show_title=False, errbar=True)
                self.census_horizontal_assesment_total(df_pop_rec, 'population', site=key, ass='% Affected recent',
                                                       specie=specie)
            # All costa brava, All affected, different species
            self.plot_mortality_assesment_zoom_modified(df_pop_all, cmap_census, 'population', '% Affected all',
                                                        type='All',
                                                        specie=specie)
            self.census_horizontal_mortality(df_pop_all, 'population', '% Affected all', type='All', specie=specie)
            self.create_histogram(df_pop_all, '% Affected all', 'Histogram population All ' + ' ' + specie + ' General',
                                  species=specie, show_title=False, errbar=True)
            self.census_horizontal_assesment_total(df_pop_all, 'population', ass='% Affected all', specie=specie)

            # All costa brava, recent affected, different species
            self.plot_mortality_assesment_zoom_modified(df_pop_rec, cmap_census, 'population', '% Affected recent',
                                                        type='Recent',
                                                        specie=specie)
            self.census_horizontal_mortality(df_pop_rec, 'population', '% Affected recent', type='Rec', specie=specie)
            self.create_histogram(df_pop_rec, '% Affected recent', 'Histogram population Recent ' + ' ' + specie + ' General',
                                  species=specie, show_title=False, errbar=True)
            self.census_horizontal_assesment_total(df_pop_rec, 'population', ass='% Affected recent', specie=specie)
        # All costa brava, All affected, all species
        self.plot_mortality_assesment_zoom_modified(df_pop_all, cmap_census, 'population', '% Affected all',
                                                    type='All')
        self.census_horizontal_mortality(df_pop_all, 'population', '% Affected all', type='All')
        self.create_histogram(df_pop_all, '% Affected all', 'Histogram population All ' + ' all ' + ' General', show_title=False, errbar=True)
        self.census_horizontal_assesment_total(df_pop_all, 'population', ass='% Affected all')

        # All costa brava, recent affected, all species
        self.plot_mortality_assesment_zoom_modified(df_pop_rec, cmap_census, 'population', '% Affected recent',
                                                    type='Recent')
        self.census_horizontal_mortality(df_pop_rec, 'population', '% Affected recent', type='Rec')
        self.create_histogram(df_pop_rec, '% Affected recent',
                              'Histogram population Recent ' + ' all ' + ' General', show_title=False, errbar=True)
        self.census_horizontal_assesment_total(df_pop_rec, 'population', ass='% Affected recent')
        print('hello')

    def plot_mortality_assesment_zoom_modified(self, df, cmap, kind, aff, type='All', coords = [3.00, 3.43, 41.74, 42.42], place='', specie='All'):
        ax, gl = self.ax_setter(lat1=coords[0], lat2=coords[1], lon1=coords[2], lon2=coords[3])
        if specie != 'All':
            df = df.loc[df['species'] == specie].sort_values('Size', ascending=False)
        else:
            df = df.sort_values('Size', ascending=False)
        asses = ax.scatter(x=df['LONG'], y=df['LAT'], c=df['Assesment ' + aff],
                           transform=ccrs.PlateCarree(), s=df['Size']*5, cmap=cmap, edgecolor='blue', linewidth=0.2, vmin=0,
                           vmax=3, zorder=10, alpha=0.7)
        cb = plt.colorbar(asses, ticks=range(0, 5), shrink=0.5, label='Assesment ' + aff)
        cb.set_ticklabels(['No Impact', 'Low Impact', 'Moderate Impact', 'High Impact'])
        plt.title('Mortality assesment ' + kind + ' ' + type + ' ' + specie)
        self.save_image('Mortality Assesment Zoom ' + kind + ' ' + type + ' ' + place + ' ' + specie)

    def mortality_assesment_modified(self, df, aff):
        for af in aff:
            df['Assesment ' + af] = df[af].apply(
                lambda y: 0 if y <= 10 else (1 if y <= 30 else (2 if y < 60 else 3)))
        colors = ['green', 'yellow', 'orange', 'red']
        cmap = LinearSegmentedColormap.from_list('Custom', colors, len(colors))
        df_sizes = df.pivot_table(index=['LAT', 'LONG'], aggfunc='size')
        df_sizes = df_sizes.reset_index()
        df_sizes = df_sizes.rename(columns={0: 'Size'})
        for i in range(0, len(df_sizes)):
            df.loc[(df['LAT'] == df_sizes['LAT'][i]) & (
                    df['LONG'] == df_sizes['LONG'][i]), 'Size'] = df_sizes['Size'][i]
        return df, cmap


    def recent_old_mortality(self):
        self.plot_mortality_assesment_zoom('Old')
        self.plot_mortality_assesment_zoom('Recent')
        species = self.df_corals['Species'].dropna().unique()
        for specie in species:
            for type in ['All', 'Old', 'Recent']:
                #General
                self.plot_yearly_mortality_assesment_zoom(species=specie, type=type, place='General')
                #Palamos
                self.plot_yearly_mortality_assesment_zoom(species=specie, type=type, coords=[2.85, 3.49, 41.72, 42.12], place='Palamós')
                #Cap de Creus
                self.plot_yearly_mortality_assesment_zoom(species=specie, type=type, coords=[3.09, 3.38, 42.21, 42.42], place='Cap de Creus')

    def mortality_assesment_census(self):
        cmap = self.mortality_assesment()
        df_census = self.df_corals.groupby('Site')['Depth', 'Species', 'Main site', 'LAT', 'LONG', 'Total colonies', 'Total affected', 'Affected old', 'Affected recent'].value_counts()
        df_census = df_census.reset_index()
        df_census = df_census.rename( columns={0:'hey'})
        df_census = df_census.drop('hey', axis=1)
        # Create dataframe containing census which are pairs of 2 measures per depth and site
        df_master = pd.DataFrame()
        cens_number = 100
        for site in df_census['Site'].unique():
            if site == 'Pta. 3 Frares':
                print('hey')
            for specie in df_census.loc[df_census['Site'] == site]['Species'].unique():
                depth_dict = {'site': site, 'depth': [], 'species':specie ,  'Main site' : str(df_census.loc[df_census['Site'] == site]['Main site'].unique()[0]), 'LAT' : float(df_census.loc[df_census['Site'] == site]['LAT'].unique()), 'LONG': float(df_census.loc[df_census['Site'] == site]['LONG'].unique()), 'entries': [], 'census': [], 'total colonies': [], 'total affected': [], 'affected old': [], 'affected recent': [], '% Affected all':[], '% Affected old':[], '% Affected recent':[]}
                depth_dict['depth'] = df_census.loc[(df_census['Site'] == site) & (df_census['Species'] == specie)]['Depth'].unique()
                for depth in depth_dict['depth']:
                    counted = df_census.loc[(df_census['Site'] == site) & (df_census['Depth'] == depth) & (df_census['Species'] == specie), 'Depth'].count()
                    depth_dict['entries'].append(counted)
                    col_ordered = df_census.loc[(df_census['Site'] == site) & (df_census['Depth'] == depth) & (df_census['Species'] == specie)].drop(['Site', 'Depth', 'Species'], axis=1).sort_values(by='Total colonies', ascending=False).reset_index(drop=True)
                    col_sum = col_ordered.cumsum()
                    totcol_cens = []
                    totaff_cens = []
                    affrec = []
                    affold = []
                    affperc_all = []
                    affperc_old = []
                    affperc_rec = []
                    idx = 0
                    #TODO falla cova fumada en depth 15
                    while idx < counted:
                        if col_sum[(col_sum['Total colonies'] < 120) & (col_sum['Total colonies'] > 80)].empty:
                            if col_sum[(col_sum['Total colonies']) > 120].empty: # Check if the value is bigger or smaller
                                idx = col_sum.index[-1]
                            else:
                                idx = col_sum.index[0]
                            totcol_cens.append(col_sum['Total colonies'][idx])
                            totaff_cens.append(col_sum['Total affected'][idx])
                            affold.append(col_sum['Affected old'][idx])
                            affrec.append(col_sum['Affected recent'][idx])
                            affperc_all.append(round((col_sum['Total affected'][idx] / col_sum['Total colonies'][idx]) * 100, 2))
                            affperc_old.append(round((col_sum['Affected old'][idx] / col_sum['Total colonies'][idx]) * 100, 2))
                            affperc_rec.append(round((col_sum['Affected recent'][idx] / col_sum['Total colonies'][idx]) * 100, 2))
                        else:
                            idx = col_sum[(col_sum['Total colonies'] < 120) & (col_sum['Total colonies'] > 80)].index[0]
                            totcol_cens.append(col_sum['Total colonies'][idx])
                            totaff_cens.append(col_sum['Total affected'][idx])
                            affold.append(col_sum['Affected old'][idx])
                            affrec.append(col_sum['Affected recent'][idx])
                            affperc_all.append(round((col_sum['Total affected'][idx]/col_sum['Total colonies'][idx])*100, 2))
                            affperc_old.append(
                                round((col_sum['Affected old'][idx] / col_sum['Total colonies'][idx]) * 100, 2))
                            affperc_rec.append(
                                round((col_sum['Affected recent'][idx] / col_sum['Total colonies'][idx]) * 100, 2))
                        if idx < counted - 1:
                            col_sum = col_ordered.iloc[idx + 1:].cumsum()
                        else:
                            idx = counted
                    depth_dict['total colonies'].append(totcol_cens)
                    depth_dict['total affected'].append(totaff_cens)
                    depth_dict['affected old'].append(affold)
                    depth_dict['affected recent'].append(affrec)
                    depth_dict['census'].append(len(totaff_cens))
                    depth_dict['% Affected all'].append(affperc_all)
                    depth_dict['% Affected old'].append(affperc_old)
                    depth_dict['% Affected recent'].append(affperc_rec)
                df_master = pd.concat([df_master, pd.DataFrame.from_dict(depth_dict)])
        df_master = df_master.explode(['total colonies', 'total affected', 'affected old', 'affected recent', '% Affected all', '% Affected old', '% Affected recent'])

        affection = ['% Affected all', '% Affected old', '% Affected recent']
        df_pop_ex = []
        for affected in affection:
            df_master = df_master.sort_values(affected, ascending=False).reset_index(drop=True)
            self.create_histogram(df_master, affected, 'Histogram Census ' + affected)
            # Població
            df_pop = df_master.groupby(['site', 'Main site', 'LAT', 'LONG', 'depth', 'species'])[affected].agg(['mean', 'std']).rename(
                columns={"mean": affected})
            df_pop_ex.append(df_pop.sort_values(affected, ascending=False).reset_index().copy())
            df_pop = df_pop.sort_values(affected, ascending=False).reset_index(drop=True)
            self.create_histogram(df_pop, affected, 'Histogram Population ' + affected, errbar=True)

        with pd.ExcelWriter('CensandPop_New.xlsx') as writer:

            df_master.to_excel(writer, sheet_name='Census')

            for df in df_pop_ex:
                df.to_excel(writer, sheet_name='Population ' + str(df.columns[6]))

        print('hello')

    def create_histogram(self,df, affected, title, site='All', species='All', errbar=False, show_title=True):
        if species!='All' and site!= 'All':
            df = df.loc[(df['species'] == species) & (df['Main site'] == site)]
        elif species!='All':
            df = df.loc[(df['species'] == species)]
        df = df.sort_values(affected, ascending=False).reset_index(drop=True)
        # Bar plot
        category_colors = ['#3faa59', '#fbfcd0', '#ffcf3d', '#ff6a6c']
        mask_no = df[affected] < 10
        mask_lo = (df[affected] >= 10) & (df[affected] < 30)
        mask_mod = (df[affected] >= 30) & (df[affected] < 60)
        mask_hi = (df[affected] >= 60)

        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_facecolor('#97b6e1')  # Light Grey #e6e6e6, Ligth Blue #8a87de
        # Bars
        ax.bar(df.index[mask_no], df[affected][mask_no], color=category_colors[0], align='edge', width=1,
               zorder=2)
        ax.bar(df.index[mask_lo], df[affected][mask_lo], color=category_colors[1], align='edge', width=1,
               zorder=2)
        ax.bar(df.index[mask_mod], df[affected][mask_mod], color=category_colors[2], align='edge', width=1,
               zorder=2)
        ax.bar(df.index[mask_hi], df[affected][mask_hi], color=category_colors[3], align='edge', width=1,
               zorder=2)
        if errbar:
            # Errorbar
            ax.errorbar(df.index[mask_no], df[affected][mask_no], yerr=df['std'][mask_no], fmt='none',
                        capsize=3, color='dimgray', zorder=3)
            ax.errorbar(df.index[mask_lo], df[affected][mask_lo], yerr=df['std'][mask_lo], fmt='none',
                        capsize=3, color='dimgray', zorder=3)
            ax.errorbar(df.index[mask_mod], df[affected][mask_mod], yerr=df['std'][mask_mod], fmt='none',
                        capsize=3, color='dimgray', zorder=3)
            ax.errorbar(df.index[mask_hi], df[affected][mask_hi], yerr=df['std'][mask_hi], fmt='none',
                        capsize=3, color='dimgray', zorder=3)

        ax.set_xticks([])
        ax.set_ylim([0, 101])
        ax.set_ylabel(affected)
        ax.axhline(y=10, color=category_colors[0], linestyle='-', zorder=1)
        ax.axhline(y=30, color=category_colors[1], linestyle='-', zorder=1)
        ax.axhline(y=60, color=category_colors[2], linestyle='-', zorder=1)
        ax.axhline(y=100, color=category_colors[3], linestyle='-', zorder=1)
        if show_title: plt.title(title)

        self.save_image(title)

    def palamos_capdecreus(self):
        #Palamos
        self.plot_mortality_assesment_zoom(coords=[2.85, 3.49, 41.72, 42.12], place='Palamós')
        #Cap de Creus
        self.plot_mortality_assesment_zoom(coords=[3.09, 3.38, 42.21, 42.42], place='Cap de Creus')


    def affected_by_ecoregion(self):
        max_years_with_MME = self.df_events['#Years with MME'].max()
        regions = self.df_events['sub-ecoregion'].unique().tolist()*max_years_with_MME
        df_aff = pd.DataFrame(regions, columns=['region']).sort_values('region').reset_index(drop=True)
        df_aff['#Years'] = list(range(1, 13)) * len(df_aff['region'].unique())
        df_aff['#Hexagons'] = 0
        for reg in self.df_events['sub-ecoregion'].unique():
            df_aff['#Hexagons'].loc[df_aff['region'] == reg] = [self.df_events['#Years with MME'].loc[(self.df_events['sub-ecoregion'] == reg) & (self.df_events['#Years with MME'] == i)].count()
                                                                           for i in range(1, max_years_with_MME + 1)]
        df_plot_ready = df_aff.groupby(['region','#Years'])['#Hexagons'].aggregate('first').unstack()
        df_plot_ready_percentage = df_plot_ready.div(df_plot_ready.sum(axis=1), axis=0)*100
        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        # Colormap
        lvTmp = np.linspace(0.3, 1.0, len(df_plot_ready.columns) - 1)
        cmTmp = matplotlib.cm.cool(lvTmp)
        newCmap = mcol.ListedColormap(cmTmp)
        df_plot_ready['sum'] = df_plot_ready[list(df_plot_ready.columns)].sum(axis=1)
        df_plot_ready.sort_values(by='sum', ascending=False, inplace=True)
        df_plot_ready.drop('sum', axis=1, inplace=True)
        # Plot order west to east
        #newCmap = sns.color_palette("ch:start=.2,rot=-.3", as_cmap=True)
        newCmap = sns.color_palette("crest", as_cmap=True)
        '''seas = ['Alboran Sea', 'Northwestern Mediterranean', 'Southwestern Mediterranean', 'Tunisian Plateau-Gulf of Sidra', 'Adriatic Sea', 'Ionian Sea', 'Aegean Sea', 'Levantine Sea']
        mapping = {sea: i for i, sea in enumerate(seas)}
        key = df_plot_ready.index.map(mapping)
        df_plot_ready = df_plot_ready.iloc[key.argsort()]'''
        df_plot_ready.plot.bar(ax=ax, stacked=True, cmap=newCmap)
        ax.legend(title='# Affected Years', bbox_to_anchor=(1, 0.5), loc='center left', fontsize='small') #, ncol=len(range(1, max_years_with_MME + 1)),
        ax.set_ylabel('# Affected Hexagons')
        plt.xticks(rotation=45, ha='right')
        labels = df_plot_ready.index
        labels = ['\n'.join(label.split()) for label in labels]
        plt.setp(ax.set_xticklabels(labels))
        self.save_image('# of affected years per total of hexagons per eco region')
        plt.clf()
        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        ax = fig.add_subplot(1, 1, 1)
        df_plot_ready_percentage.plot.bar(ax=ax, stacked=True, cmap=newCmap)
        ax.legend(title='# Affected Years', ncol=len(range(1, max_years_with_MME + 1)), bbox_to_anchor=(0, 1),
                  loc='lower left', fontsize='small')
        ax.set_ylabel('% Affected Hexagons')
        plt.xticks(rotation=30, ha='right')
        plt.setp(ax.set_xticklabels(labels))
        self.save_image('# of affected years per percentage of hexagons per eco region')
        plt.clf()
        print('proba')

    @staticmethod
    def ax_setter(lat1=-9.5, lat2=37., lon1=28., lon2=50., subplot=False):
        """
        Creates the axes where the map will be plotted selecting the coordinates to properly represent
        the Mediterranean sea and plots and colors the land and sea.

        Returns
        -------
        ax : Axes matplotlib
            the axes in which the data will be plotted
        gl : Gridlines
            the gridlines of the plot featured to divide the latitude and longitude
        """
        import owslib
        if not subplot:
            rows = 1
            columns = 1
        else:
            rows = 2
            columns = 1

        fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))

        ax = fig.add_subplot(rows, columns, 1, projection=ccrs.Mercator())
        ax.set_extent([lat1, lat2, lon1, lon2], crs=ccrs.PlateCarree())
        #ax.add_feature(cf.OCEAN)
        #ax.add_feature(cf.LAND)
        ax.add_wms(wms='http://ows.emodnet-bathymetry.eu/wms',
                   layers=['coastlines']) # Poner emodnet bathymetry getcapabilities for layers , 'emodnet:mean_atlas_land'
        #coast = cf.GSHHSFeature(scale='full')
        #ax.add_feature(coast)
        #ax.coastlines(resolution='10m')
        ax.add_feature(cf.BORDERS, linestyle=':', alpha=1)

        gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=1, color='grey', alpha=0.3, linestyle='--',
                          draw_labels=True)
        gl.top_labels = False
        gl.left_labels = True
        gl.right_labels = False
        gl.xlines = True
        # gl.xlocator = mticker.FixedLocator([120, 140, 160, 180, -160, -140, -120])
        # gl.ylocator = mticker.FixedLocator([0, 20, 40, 60])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        # gl.xlabel_style = {'color': 'red', 'weight': 'bold'}
        p = ax.get_window_extent()
        '''plt.annotate('Source: T-MEDNet MHW Tracker / Generated using E.U. Copernicus Marine Service information',
                     xy=(-0.2, -0.3), xycoords=p, xytext=(0.1, 0),
                     textcoords="offset points",
                     va="center", ha="left")'''
        # TODO quitar cuando no toca
        '''plt.annotate('t-mednet.org', xy=(0.01, 0.03), xycoords=p, xytext=(0.1, 0),
                     textcoords="offset points",
                     va="center", ha="left", alpha=0.5)
        '''
        if not subplot:
            return ax, gl
        else:
            return ax, gl, fig



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