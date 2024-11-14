import pandas as pd
import numpy as np
import os
import csv
import re
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class SeaSampler():

    def __init__(self, path, type, output_file):
        if type == 'metadata':
            columns = ['User', 'Sensor', 'Dive', 'Date Range', 'Latitude', 'Longitude', 'Duration', 'Tmin',
                       'Tmax', 'Tsurface', 'Depth']
            df = pd.DataFrame(columns=columns)
            # path = '../src/input_files/SeaSampler'
            df, bad_list = self.dir_reader(df, path, self.dict_creator)
            df.to_excel('../src/output_files/' + output_file + '.xlsx')
            self.save_txt('bad_entries_' + output_file, bad_list)

        if type == 'control depth':
            df, bad_list = self.dir_reader(df='bad', path=path, func=self.check_depths)
            self.save_txt('bad_depth_entries', bad_list)
        if type == 'plots':
            df, bad_list = self.dir_reader(df=pd.DataFrame(), path=path, func=self.mega_dataframe)
            self.temp_depth_data = df.sort_values(by='date')
            print('he')

    def open_netcdf(self, path, bad, bad2, bad3):
        # Limits of the catalan coast
        lat_min = 41.6600
        lat_max = 42.1104
        lon_min = 2.7800
        lon_max = 3.2680
        ds = xr.open_dataset(path)
        df = ds.to_dataframe().reset_index()
        self.netcds = ds['analysed_sst']-273.15
        df_filtrado = df[
            (df['lat'] >= lat_min) &
            (df['lat'] <= lat_max) &
            (df['lon'] >= lon_min) &
            (df['lon'] <= lon_max)
            ]
        df_filtrado['analysed_sst'] = df_filtrado['analysed_sst'] - 273.15
        if hasattr(self, 'df_surface_mean'):
            self.df_surface_mean = pd.concat([self.df_surface_mean, df_filtrado], ignore_index=True)
        else:
            self.df_surface_mean = df_filtrado.copy()

        return 'bad', 'bad'

    def create_map(self):
        # Crear la figura y los ejes con la proyección adecuada
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

        # Configurar la proyección y agregar costas y fronteras
        ax.coastlines(resolution="10m")
        ax.add_feature(cfeature.BORDERS, linestyle=':')

        # Plotear los datos de temperatura
        temp_plot = self.netcds.plot(
            ax=ax,
            transform=ccrs.PlateCarree(),  # Transformación para coordenadas geográficas
            cmap="coolwarm",  # Paleta de colores para la temperatura
            cbar_kwargs={'label': 'Temperatura (°C)'}  # Etiqueta de la barra de color
        )

        # Configurar límites del área del Mediterráneo
        ax.set_extent([-5, 40, 30, 45], crs=ccrs.PlateCarree())

        # Título y visualización
        plt.title("Temperatura del Mediterráneo")
        plt.savefig('../src/output_images/mapa_temp_mediterrani.png')

    def sst_daily(self):
        df_sst_daily = self.df_surface_mean.groupby('time').mean().reset_index()
        df_sst_daily['time'] = df_sst_daily['time'].dt.strftime('%d-%m')
        return df_sst_daily

    def plot_surface_mean(self):
        date_start = '2024-09-01'
        date_end = '2024-10-01'
        df_sst_daily = self.sst_daily()
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.plot(df_sst_daily['time'], df_sst_daily['analysed_sst'], color='k', label='Surface Mean of the area')
        color = ['blue', 'red', 'yellow', 'green']
        site = ['Tossa', 'Boreas', 'Medes', 'Ullastres']
        i = 0
        # Sets the index to time to reindex the following data
        df_sst_daily.set_index('time', inplace=True)
        for data in self.data_list:
            data['date'] = pd.to_datetime(data['date'])
            data = data[(data['date'] >= date_start) & (data['date'] <= date_end)]
            data['timeless'] = data['date'].dt.strftime('%d-%m')
            data = data.sort_values(by='date')
            data = data.groupby('timeless').max()
            data = data.reindex(df_sst_daily.index)
            data = data.reset_index()


            ax.plot(data['time'], data['temperature(c)'], color=color[i], label=site[i], marker='o')
            i += 1
        ax.set_xticklabels(data['time'], rotation=45)
        ax.legend(loc='upper right')
        plt.savefig('../src/output_images/Mean surface and sites_v1.png')
    def add_data_list(self, path):
        if hasattr(self, 'data_list'):
            df, bad_list = self.dir_reader(df=pd.DataFrame(), path=path, func=self.mega_dataframe)
            self.data_list.append(df.sort_values(by='date'))
        else:
            self.data_list = []
            self.data_list.append(self.temp_depth_data)
            df, bad_list = self.dir_reader(df=pd.DataFrame(), path=path, func=self.mega_dataframe)
            self.data_list.append(df.sort_values(by='date'))

    @staticmethod
    def save_txt(filename, my_list):
        with open('../src/output_files/' + filename + ".txt", "w") as file:
            for item in my_list:
                file.write(item + "\n")

    @staticmethod
    def dms_to_decimal(coordenada):
        # Usar expresiones regulares para extraer los grados, minutos y segundos
        match = re.match(r"(-?\d+)º(-?\d+)'(-?[\d.]+)\"([NSEW])", coordenada)

        if match:
            # Convertir a enteros o flotantes según corresponda
            grados = int(match.group(1))
            minutos = int(match.group(2))
            segundos = float(match.group(3))
            direccion = match.group(4)

            # Convertir a decimal
            decimal = grados + (minutos / 60) + (segundos / 3600)

            # Hacer negativo si es S o W y grados son positivos
            if direccion in ['S', 'W']:
                decimal = -abs(decimal)

            return decimal
        else:
            raise ValueError("El formato de la coordenada no es válido.")

    def prepare_radar_plot(self, labels):
        # Prepare the labels

        num_vars = len(labels)

        # Crear el gráfico de radar
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))

        # Convertir etiquetas en ángulos para el gráfico de radar
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        return ax, angles

    # TODO add the possibility to plot multiple sites
    def radar_plot(self):
        if hasattr(self, 'data_list'):
            dip = 0
            for data in self.data_list:
                if data['depth(m)'].max() > dip:
                    dip = data['depth(m)'].max().round()
            labels = range(1, int(dip) + 1, 1)
            ax, angles = self.prepare_radar_plot(labels)
            color = ['blue', 'red', 'yellow', 'green']
            site = ['Tossa', 'Boreas', 'Medes', 'Ullastres']
            i = 0
            for data in self.data_list:
                data['depth(m)'] = data['depth(m)'].round()
                data_mean = data.groupby(by='depth(m)', as_index=False)['temperature(c)'].mean()
                # First add nan if depth is lower than max
                if data_mean['depth(m)'].iloc[-1] != dip:
                    fdepth = data_mean['depth(m)'].iloc[-1]
                    diff = dip - fdepth
                    for n in range(1, int(diff) + 1, 1):
                        new_row = pd.DataFrame({'depth(m)': [fdepth + n], 'temperature(c)': [np.nan]})
                        data_mean = pd.concat([data_mean, new_row], ignore_index=True)
                # Repetir el primer valor al final para cerrar el gráfico
                data_mean = pd.concat([data_mean, pd.DataFrame([data_mean.iloc[0]])], ignore_index=True)

                ax.plot(angles, data_mean['temperature(c)'], color=color[i], linewidth=2,
                        label='Average temperature - ' + site[i])

                # Rellenar el área bajo la curva
                ax.fill(angles, data_mean['temperature(c)'], color=color[i], alpha=0.1)
                i += 1
        else:
            # Prepare the data for the plot by rounding the depths to integers and  calculating the mean
            data = self.temp_depth_data.copy()
            data['depth(m)'] = data['depth(m)'].round()
            data_mean = data.groupby(by='depth(m)', as_index=False)['temperature(c)'].mean()
            labels = data['depth(m)'].unique()
            ax, angles = self.prepare_radar_plot(labels)

            # Repetir el primer valor al final para cerrar el gráfico
            data_mean = pd.concat([data_mean, pd.DataFrame([data_mean.iloc[0]])], ignore_index=True)

            ax.plot(angles, data_mean['temperature(c)'], color='blue', linewidth=2, label='Average temperature - Tossa')

            # Rellenar el área bajo la curva
            ax.fill(angles, data_mean['temperature(c)'], color='blue', alpha=0.1)

        # Configuración de etiquetas y leyenda
        #ax.set_yticklabels(['haha', 'hehe'])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color='skyblue', fontsize=12)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.savefig('../src/output_images/radar_combo4_v1.png')

    def mega_dataframe(self, file_path, file_name, df, bad_list):
        df = df.append(pd.read_csv(file_path))
        return df, 'bad'

    # TODO convertir date a timestamp o datetime y hacer caso a chatgpt
    def plot_depthvstemp(self, filename):
        self.temp_depth_data['date'] = pd.to_datetime(self.temp_depth_data['date'])
        # Probamos un resample para suavizar las lineas
        self.temp_depth_data = self.temp_depth_data.resample('T', on='date').mean().reset_index()
        # Usar solo datos de ciertos dias self.temp_depth_data.loc[self.temp_depth_data['date'] <= '2024-09-20']
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.plot(self.temp_depth_data['date'], self.temp_depth_data['temperature(c)'])
        ax2 = ax.twinx()
        ax2.plot(self.temp_depth_data['date'], self.temp_depth_data['depth(m)'], color='tab:orange')
        ax2.invert_yaxis()
        plt.savefig('../src/output_images/' + filename + '.png')
        print('alo')

    # TODO work on using *args and **kwargs to make the functions more flexible
    def check_depths(self, file_path, file_name, df, bad_list, *args):
        df = pd.read_csv(file_path, skiprows=16)
        df['depth(m)'] = - df['depth(m)']
        # devuelve las entradas que estan por debajo de un metro de profundidad
        if df.loc[df['depth(m)'] < 1].empty:
            text = 'Depth ok in: ' + file_name
            bad_list.append(text)
            df.to_csv('../src/input_files/SeaSampler Boreas/' + file_name + '.csv', index=False, sep=',')
            return df, bad_list
        else:
            df = df.loc[df['depth(m)'] >= 1]
            df.to_csv('../src/input_files/SeaSampler Boreas/' + file_name + '.csv', index=False, sep=',')
            text = 'ERROR DEPTH in: ' + file_name
            bad_list.append(text)
            return df, bad_list
        print('he')
        return df, 'bad'

    def dict_creator(self, file_path, file_name, df, bad_list):
        # Gets the first temperature record, estimated to be the surface record
        df_quick = pd.read_csv('../src/input_files/SeaSampler_corrected/' + file_name + '.csv')
        if df_quick.empty:
            print('ha')
            bad_list.append('Empty file: ' + file_name)
            return df, bad_list
        tsurface = df_quick['temperature(c)'][0]
        min_temp = df_quick['temperature(c)'].min()
        max_temp = df_quick['temperature(c)'].max()
        with open(file_path, newline='') as csvfile:
            # Crear el lector de CSV
            csvreader = csv.reader(csvfile)
            primeras_lineas = []
            num_lineas = 16
            # Leer y guardar las primeras 'num_lineas'
            for i, row in enumerate(csvreader):
                if i < num_lineas:
                    primeras_lineas.append(row)
                else:
                    break
            primeras_lineas = [','.join(item) for item in primeras_lineas if item]
            # Selecciona los items para montar el dict
            user = primeras_lineas[1].split(':', 1)[1][1:]
            sensor = primeras_lineas[2].split(':', 1)[1][1:]
            dive = primeras_lineas[3].split(':', 1)[1][1:]
            date = primeras_lineas[4].split(':', 1)[1][1:]
            years = [date.split('-')[0], date.split('-')[3]]
            if (years[0].lstrip() != years[1].lstrip()) | (years[0].lstrip() == '1970') | (years[1].lstrip() == '1970'):
                print('Discrepancy in years in file: ' + file_name)
                bad_list.append('Discrepancy on years on: ' + file_name)
                return df, bad_list
            bad_lat = primeras_lineas[5].split(':', 1)[1][1:].split(',')[0]
            if bool(re.match(r"^-?\d+º-?\d+'-?\d+(\.\d+)?\"[NSEW]$", bad_lat)):
                lat = self.dms_to_decimal(bad_lat)
            else:
                lat = float(bad_lat)
            bad_lon = primeras_lineas[5].split(':', 1)[1][1:].split(',')[1]
            if bool(re.match(r"^-?\d+º-?\d+'-?\d+(\.\d+)?\"[NSEW]$", bad_lon)):
                lon = self.dms_to_decimal(bad_lon)
            else:
                lon = float(bad_lon)
            dur = primeras_lineas[7].split(':', 1)[1][1:]
            # min_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[0].split(' ', 1)[0]
            # max_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[1].split(' ', 1)[1].split(' ', 1)[0]
            depth = int(-float(primeras_lineas[9].split(':', 1)[1].split(' ')[1]))
            dict = {'User': user, 'Sensor': sensor, 'Dive': dive, 'Date Range': date, 'Latitude': lat, 'Longitude': lon,
                    'Duration': dur, 'Tmin': min_temp, 'Tmax': max_temp, 'Tsurface': tsurface, 'Depth': depth}
            df = df.append(dict, ignore_index=True)
            return df, bad_list

    def dir_reader(self, df, path, func):
        bad_list = []
        for file in os.listdir(path):  # use the directory name here
            file_name, file_ext = os.path.splitext(file)
            print(file_name)
            file_path = path + '/' + file
            if (file_ext == '.csv') | (file_ext == '.nc'):
                df, bad_list = func(file_path, file_name, df, bad_list)
        return df, bad_list
