import pandas as pd
import numpy as np
import os
import csv
import re
#TODO convertir depth en positiu

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

columns = ['User', 'Sensor', 'Dive', 'Date Range', 'Latitude', 'Longitude', 'Duration', 'Tmin', 'Tmax', 'Depth']
df = pd.DataFrame(columns=columns)
for file in os.listdir('../src/input_files/TODO'):  # use the directory name here

    file_name, file_ext = os.path.splitext(file)
    print(file_name)
    if file_name == "Diver1_SeaScale_2024-08-05T16_07_55_2024-09-05T12_53_55(1)":
        print('ups')
    file_path = '../src/input_files/TODO/' + file
    if file_ext == '.csv':
        with open(file_path, newline='') as csvfile:
            # Crear el lector de CSV
            csvreader = csv.reader(csvfile)

            # Lista para almacenar las primeras líneas
            primeras_lineas = []

            # Número de líneas que quieres leer
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
            bad_lat = primeras_lineas[5].split(':', 1)[1][1:].split(',')[0]
            if bool(re.match(r"^-?\d+º-?\d+'-?\d+(\.\d+)?\"[NSEW]$", bad_lat)):
                lat = dms_to_decimal(bad_lat)
            else:
                lat = float(bad_lat)
            bad_lon = primeras_lineas[5].split(':', 1)[1][1:].split(',')[1]
            if bool(re.match(r"^-?\d+º-?\d+'-?\d+(\.\d+)?\"[NSEW]$", bad_lon)):
                lon = dms_to_decimal(bad_lon)
            else:
                lon = float(bad_lon)
            dur = primeras_lineas[7].split(':', 1)[1][1:]
            min_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[0].split(' ', 1)[0]
            max_temp = primeras_lineas[8].split(':', 1)[1][1:].split(')', 1)[1].split(' ', 1)[1].split(' ', 1)[0]
            depth = primeras_lineas[9].split(':', 1)[1].split(' ')[1]
            dict = {'User': user, 'Sensor': sensor, 'Dive': dive, 'Date Range': date, 'Latitude': lat, 'Longitude': lon, 'Duration': dur, 'Temp. Min.': min_temp, 'Temp. Max.': max_temp, 'Depth': depth}
            df = df.append(dict, ignore_index=True)


df.to_excel('../src/output_files/list_seascale_dives.xlsx')
