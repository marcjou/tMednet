import pandas as pd
import numpy as np
import os
import csv
import re

class SeaSampler():

    def __init__(self, path, type, output_file):
        if type == 'metadata':
            columns = ['User', 'Sensor', 'Dive', 'Date Range', 'Latitude', 'Longitude', 'Duration', 'Tmin',
                       'Tmax', 'Depth']
            df = pd.DataFrame(columns=columns)
            # path = '../src/input_files/SeaSampler'
            df, bad_list = self.dir_reader(df, path, self.dict_creator)
            df.to_excel('../src/output_files/' + output_file +  '.xlsx')
            self.save_txt('bad_entries_' + output_file, bad_list)

        if type == 'control depth':

            print('yes')

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

    def dict_creator(self, file_path, file_name, df, bad_list):
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
            min_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[0].split(' ', 1)[0]
            max_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[1].split(' ', 1)[1].split(' ', 1)[0]
            depth = int(-float(primeras_lineas[9].split(':', 1)[1].split(' ')[1]))
            dict = {'User': user, 'Sensor': sensor, 'Dive': dive, 'Date Range': date, 'Latitude': lat, 'Longitude': lon,
                    'Duration': dur, 'Tmin': min_temp, 'Tmax': max_temp, 'Depth': depth}
            df = df.append(dict, ignore_index=True)
            return df, bad_list

    def dir_reader(self, df, path, func):
        bad_list = []
        for file in os.listdir(path):  # use the directory name here
            file_name, file_ext = os.path.splitext(file)
            print(file_name)
            if file_name == "Diver1_SeaScale_2024-08-05T16_07_55_2024-09-05T12_53_55(1)":
                print('ups')
            file_path = path +'/' + file
            if file_ext == '.csv':
                df, bad_list = func(file_path, file_name, df, bad_list)
        return df, bad_list




