import numpy as np
import pandas as pd
from datetime import datetime


df_5 = pd.read_csv('../src/Medsharks/159_20160820-08_20220102-16_05.txt', sep='\t', header=0, names=['Date', 'Time', '5'])
df_10 = pd.read_csv('../src/Medsharks/159_20210706-12_20211020-09_10.txt', sep='\t', header=0, names=['Date', 'Time', '10'])
df_15 = pd.read_csv('../src/Medsharks/159_20160416-08_20211029-09_15.txt', sep='\t', header=0, names=['Date', 'Time', '15'])
df_20 = pd.read_csv('../src/Medsharks/159_20180127-09_20211029-09_20.txt', sep='\t', header=0, names=['Date', 'Time', '20'])
df_25 = pd.read_csv('../src/Medsharks/159_20210706-12_20211029-09_25.txt', sep='\t', header=0, names=['Date', 'Time', '25'])
df_30 = pd.read_csv('../src/Medsharks/159_20210706-12_20211029-09_30.txt', sep='\t', header=0, names=['Date', 'Time', '30'])
df_33 = pd.read_csv('../src/Medsharks/159_20160430-08_20170109-03_33.txt', sep='\t', header=0, names=['Date', 'Time', '33'])
df_36 = pd.read_csv('../src/Medsharks/159_20161105-09_20220102-04_36.txt', sep='\t', header=0, names=['Date', 'Time', '36'])

list_df = [df_5, df_10, df_15, df_20, df_25, df_30, df_33, df_36]

for i in list_df:
    i['Real'] = i['Date'] + ' ' + i['Time']
    print('Got there')
    i['Real'] = pd.to_datetime(i['Real'], dayfirst=True)
    print('That one was heavy')
    i.set_index(i['Real'], inplace=True)
    i.drop(['Date', 'Time', 'Real'], axis=1, inplace=True)
    print('Got here')

'''
df_5.set_index(df_5['Date'], inplace=True)
df_10.set_index(df_10['Date'], inplace=True)
df_15.set_index(df_15['Date'], inplace=True)
df_20.set_index(df_20['Date'], inplace=True)
df_25.set_index(df_25['Date'], inplace=True)
df_30.set_index(df_30['Date'], inplace=True)
df_33.set_index(df_33['Date'], inplace=True)
df_36.set_index(df_36['Date'], inplace=True)


df_5.drop('Date', axis=1, inplace=True)
df_10.drop('Date', axis=1, inplace=True)
df_15.drop('Date', axis=1, inplace=True)
df_20.drop('Date', axis=1, inplace=True)
df_25.drop('Date', axis=1, inplace=True)
df_30.drop('Date', axis=1, inplace=True)
df_33.drop('Date', axis=1, inplace=True)
df_36.drop('Date', axis=1, inplace=True)
'''

df_total = pd.merge(df_5, df_10, how='outer', left_index=True, right_index=True)

for i in list_df[2:]:
    df_total =pd.merge(df_total, i, how='outer', left_index=True, right_index=True)

df_total['Time'] = df_total.index.strftime('%H:%M:%S')
df_total['Date'] = df_total.index.strftime('%d/%m/%Y')

df_total = df_total[['Date', 'Time', '5', '10', '15', '20', '25', '30', '33', '36']]

for i in df_total:
    if i.index.timestamp() % 3600 == 0:
        pass

df_total.reset_index(drop=True, inplace=True)

df_total.to_csv('../src/output_files/Med_159.txt', sep='\t', index=False)
print('hola')
