import csv
import os
import pandas as pd

cwd = os.getcwd()
#print(cwd)

for file in os.listdir('../src/Mallorca'):  # use the directory name here

    file_name, file_ext = os.path.splitext(file)
    file_path = '../src/Mallorca/' + file
    if file_ext == '.csv':
        df = pd.read_csv(file_path, names=['num', 'date', 'val'], skiprows=2, sep=',', usecols=[0, 1, 2])
        del df['num']
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%d/%m/%Y %H:%M:%S')
        df_meta = pd.read_csv(file_path, skiprows=1, nrows=1, header=None)
        meta = df_meta.to_string(header=False,
                                index=False,
                                index_names=False)
        smeta = pd.DataFrame({'date': meta, 'val': ''}, index=[0])
        df_final = pd.concat([smeta,df.loc[:]]).reset_index(drop=True)
        df_final.to_csv('../src/Mallorca/final/' + file_name + '.txt', header=None, index=None, sep='\t', mode='a')
