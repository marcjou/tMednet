import numpy as np
import pandas as pd
import os
import folium
import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import cartopy.feature as cfeature


import cartopy.crs as ccrs
import matplotlib.dates as dates
import matplotlib.dates as mdates
from matplotlib.figure import Figure


class SensorData():

    def __init__(self, filename, type):
        # For test "/home/marc/Projects/Mednet/tMednet/src/input_files/prueba_seascale.csv"

        if type == 'site':
            # Load csv as DataFrame directly with its header
            self.data = [pd.read_csv(filename, sep=',', header=9)]
            # Reads the file and stores the metadata
            with open(filename) as f:
                content = f.readlines()
                self.utc = [content[7][-8:-2]]
                self.sensor = [content[4][7:-1]]
                self.dive = [content[6][5:-1]]
                self.duration = [datetime.strptime(content[10][10:-4], '%H:%M:%S').time()]
                self.duration_seconds = [(self.duration.hour*60 + self.duration.minute)*60 + self.duration.second]
            self.__convert_to_utc()
        elif type == 'multi_center':
            # Load csv as DataFrame directly with its header
            self.data = [pd.read_excel(filename, skiprows=2, usecols='B:E')]
            self.place_coordinates()
        elif type == 'multi_site':
            # Loads multiple csv as they have been uploaded
            self.__read_mutiple_csv(filename)

    def __read_mutiple_csv(self, filenames):
        self.data = []
        self.utc = []
        self.sensor = []
        self.dive = []
        self.duration = []
        self.duration_seconds = []
        for filename in filenames:
            self.data.append(pd.read_csv(filename, sep=',', header=9))
            # Reads the file and stores the metadata
            with open(filename) as f:
                content = f.readlines()
                self.utc.append(content[7][-8:-2])
                self.sensor.append(content[4][7:-1])
                self.dive.append(content[6][5:-1])
                self.duration.append(datetime.strptime(content[10][10:-4], '%H:%M:%S').time())
                self.duration_seconds.append((self.duration.hour * 60 + self.duration.minute) * 60 + self.duration.second)
        self.__convert_to_utc()
    def __convert_to_utc(self):
        #TODO se deberia mostrar todo siempre en UTC 0??
        for i in len(self.data):
            # Converts date column to datetime object and transforms it to UTC 00:00
            if self.utc[i][0] == '+':
                self.data[i]['date'] = pd.to_datetime(self.data[i]['date'],
                                                   format="%Y-%m-%d %H:%M:%S") - timedelta(hours=float(self.utc[i][1:3]),
                                                                                           minutes=float(self.utc[i][4:6]))
            else:
                self.data[i]['date'] = pd.to_datetime(self.data[i]['date'],
                                                   format="%Y-%m-%d %H:%M:%S") + timedelta(hours=float(self.utc[i][1:3]),
                                                                                           minutes=float(self.utc[i][4:6]))

    def plot_temperature_depth(self):

        # Create ticks and labels for x axis
        start_round_time = self.data['date'][0].floor('15min')
        end_round_time = self.data['date'][len(self.data) - 1].ceil('15min')
        ticks = pd.date_range(start_round_time, end_round_time, freq='15min')

        # Starts the figures and axes
        fig, ax1 = plt.subplots()
        ax1.set_ylabel('Temperature (ºC)', color='tab:blue')
        ax2 = ax1.twinx()
        ax2.set_ylabel('Depth (m)', color='tab:red')

        # Plots the temperature and depth
        self.data.plot(x='date', y='temperature(ºC)', ax=ax1)
        self.data.plot(x='date', y='depth(m.)', color='tab:red', ax=ax2)
        ax1.xaxis.set_ticks(ticks)
        plt.xticks(ticks)
        plt.xlabel('Time')
        ax1.set_xlabel('Time')

        # Sets a grid showing the depths levels
        plt.grid(color='gray', linestyle='--', linewidth=0.3)

        self.__class__.__save_image(self.dive + '_' +
                                    self.data['date'][0].strftime('%d-%m-%Y'))

    def create_map(self):
        # Coordenadas del centro del mapa (aproximadamente el centro entre Gibraltar y la frontera francesa)
        map_center = [38, -2]

        # Crear el mapa usando Folium, centrado en la región y con un zoom adecuado
        m = folium.Map(location=map_center, zoom_start=6, tiles='OpenStreetMap')

        return m

    def place_coordinates(self, points=False):
        m = self.create_map()

        if points:
            for name, coords in points:
                folium.Marker(coords).add_to(m)
        else:
            # Itera en la lista y crea el mapa con sus contenidos
            for index, row in self.data.iterrows():
                popup_content = """<b>Centro:</b> """ + row['Centro'] + """<br>
                        <b>Ubicación:</b> """ + row['Localidad'] + """<br>
                        <b>Coordenadas:</b> """ + str(row['Lat']) + """, """ + str(row['Lon']) + """<br>
                        <b>Número de registros: </b>
                                    """
                coords = tuple([row['Lat'], row['Lon']])
                folium.Marker(coords, popup=folium.Popup(popup_content, max_width=300, min_width=150), tooltip=row['Centro']).add_to(m)

        # Guardar el mapa en un archivo HTML
        m.save('../mapa_centros_seascale.html')

    @staticmethod
    def __save_image(savefile):
        plt.savefig('/home/marc/Projects/Mednet/tMednet/src/' + savefile + '.png')

    @staticmethod
    def __custom_round(x, base=0.25):
        return base * round(float(x) / base)

    def __transform_to_columns(self, new_df=False):
        # Pivots table to convert date, temp, depth df to date index and depths columns rounded default=0.25
        if new_df:
            data_copy = new_df
        else:
            data_copy = self.data.copy()
        data_copy['depth(m.)'] = data_copy['depth(m.)'].apply(lambda x: self.__class__.__custom_round(x))
        data_copy = data_copy.pivot('date', 'depth(m.)')
        data_copy.columns = data_copy.columns.droplevel(0)
        return data_copy

    def __concat_files(self, path):
        diff = ''
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        for file in csv_files:
            df = pd.read_csv(file, sep=',', header=9)
            if diff == '':
                diff = self.__transform_to_columns(df)
            else:
                duf2 = self.__transform_to_columns(df)
                diff = pd.concat([diff, duf2], axis=0, keys=['diff', 'duf2'], join='inner')
        return diff

    def stratification_plot(self):
        # Open all the files to use on the stratification plot
        df = self.__concat_files()
        fig, ax1 = plt.subplots()
        # Create the different levels to show on the plot (2) and on the colorbar (1)
        levels = np.arange(np.floor(df.min()), df.max(), 1)
        levels2 = np.arange(np.floor(df.min()), df.max(), 0.1)
        cf = ax1.contourf(df.index, df.columns, df.values.T, 256, extend='both', cmap='RdYlBu_r',
                                  levels=levels2)

        cb = plt.colorbar(cf, ax=ax1, label='Temperature (ºC)', ticks=levels)
        print('placeholder')
