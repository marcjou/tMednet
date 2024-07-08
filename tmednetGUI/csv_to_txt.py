import csv
import os
import pandas as pd

cwd = os.getcwd()
#print(cwd)

for file in os.listdir('../src/input_files/MARZOA procesar'):  # use the directory name here

    file_name, file_ext = os.path.splitext(file)
    file_path = '../src/input_files/MARZOA procesar/' + file
    if file_ext == '.csv':
        df = pd.read_csv(file_path, names=['date', 'val'], skiprows=2, sep=',', usecols=[1, 2], dayfirst=True)
        #df = pd.read_csv(file_path, sep=',', dayfirst=True)
        #del df['num']
        # Change depending of file
        #df['datetime'] = df['date'] + ' ' + df['time']
        #df['date'] = df['date'].str.replace('.', ':')
        print(file_name)
        df['date'] = df['date'].str.replace('.', ':')
        #del df['datetime']
        #del df['time']
        df['date'] = pd.to_datetime(df['date'], dayfirst=False)
        df['date'] = df['date'].dt.strftime('%d/%m/%y %H:%M:%S')
        #meta = '"N.º"	"Fecha"	"Tiempo, GMT+01:00"	"Temp, °C (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Intensidad, lux (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Acoplador adjunto (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Host conectado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Parado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Final de archivo (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"'
        df_meta = pd.read_csv(file_path, skiprows=1, nrows=1, header=None)
        meta = df_meta.to_string(header=False,
                                index=False,
                                index_names=False)
        smeta = pd.DataFrame({'date': meta, 'val': ''}, index=[0])
        df_final = pd.concat([smeta,df.loc[:]]).reset_index(drop=True)
        df_final.to_csv('../src/input_files/MARZOA procesar/' + file_name + '.txt', header=None, index=None, sep='\t', mode='a')
