import csv
import os
import pandas as pd

cwd = os.getcwd()
#print(cwd)

for file in os.listdir('../src/input_files/Mes tanda'):  # use the directory name here

    file_name, file_ext = os.path.splitext(file)
    file_path = '../src/input_files/Mes tanda/' + file
    if file_ext == '.csv':
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            df = pd.read_csv(f, sep=';', names=['date', 'time', 'val'], skiprows=1, dayfirst=True)
        df = df.reset_index()
        df = df.drop(columns=df.columns[0])
        df['date'] = df['date'] + ' ' + df['time']
        df = df.drop(columns='time')
        #df = pd.read_csv(file_path, sep=',', dayfirst=True)
        #del df['num']
        # Change depending of file
        #df['datetime'] = df['date'] + ' ' + df['time']
        #df['date'] = df['date'].str.replace('.', ':')
        print(file_name)
        #df['date'] = df['date'].str.replace('.', ':')
        #del df['datetime']
        #del df['time']
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        dofus = df['date'].copy()
        df['date'] = dofus.dt.strftime('%d/%m/%y')
        df.insert(loc=1, column='time', value=dofus.dt.strftime('%H:%M:%S'))
        df = df.drop(df[df['val'] == -9999.0].index)
        #meta = '"N.º"	"Fecha"	"Tiempo, GMT+01:00"	"Temp, °C (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Intensidad, lux (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Acoplador adjunto (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Host conectado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Parado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Final de archivo (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"'
        #df_meta = pd.read_csv(file_path, skiprows=1, nrows=1, header=None)
        #meta = df_meta.to_string(header=False, index=False, index_names=False)
        meta = '''"N.º"	"Fecha"	"Tiempo, GMT+02:00"	"Temp, °C (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Acoplador separado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Acoplador adjunto (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Host conectado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Parado (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"	"Final de archivo (LGR S/N: XXXXXXXX, SEN S/N: XXXXXXXX)"'''
        smeta = pd.DataFrame({'index' : '', 'date': meta, 'time': '', 'val': ''}, index=[0])
        df_final = pd.concat([smeta,df.loc[:].reset_index()]).reset_index(drop=True)
        #df_final.insert(loc=0, column='Nº', value=df_final.index)
        #df_final = df.loc[:].reset_index(drop=True)
        df_final.to_csv('../src/input_files/Mes tanda/' + file_name + '.txt', header=None, index=None, sep='\t', mode='a')
