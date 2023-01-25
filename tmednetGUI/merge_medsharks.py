import numpy as np
import pandas as pd
from datetime import datetime


df_15 = pd.read_csv('../src/Medsharks/165_20210617-08_20211106-10_15.txt', sep='\t', header=0, names=['Date', 'Time', '15'])
df_30 = pd.read_csv('../src/Medsharks/165_20210617-08_20211106-09_30.txt', sep='\t', header=0, names=['Date', 'Time', '30'])
df_42 = pd.read_csv('../src/Medsharks/165_20210617-08_20211106-10_42.txt', sep='\t', header=0, names=['Date', 'Time', '42'])

list_df = [df_15, df_30, df_42]

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

df_total = pd.merge(df_15, df_30, how='outer', left_index=True, right_index=True)

for i in list_df[2:]:
    df_total =pd.merge(df_total, i, how='outer', left_index=True, right_index=True)

df_total['Time'] = df_total.index.strftime('%H:%M:%S')
df_total['Date'] = df_total.index.strftime('%d/%m/%Y')

df_total = df_total[['Date', 'Time', '15', '30', '42']]
'''
for i in df_total:
    if i.index.timestamp() % 3600 == 0:
        pass
'''
df_total.reset_index(drop=True, inplace=True)

df_total.to_csv('../src/output_files/Med_165.txt', sep='\t', index=False)
print('hola')
