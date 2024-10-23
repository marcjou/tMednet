import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
df = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202409.txt', sep='\t')
# Recover year and month
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
# Pin point the data for only the JAS months
df_ordered = df.loc[(df['Month'] >= 7) & (df['Month'] <= 9)]
df_ordered['Time'] = pd.to_datetime(df_ordered['Time'], format='%H:%M:%S').dt.time
# Se crea una nueva columna con solo el mes y dia y hora como importante, ignorando por completo el año, normalizandolo al año 2013
df_ordered['WholeDate'] = df_ordered.apply(lambda row: datetime.combine(row['Date'].date(), row['Time']), axis=1)
df_ordered['normal_date'] = df_ordered['WholeDate'].apply(lambda x: x.replace(year=2013))
# normal date no times
df_ordered['normal_date_timeless'] = df_ordered['Date'].apply(lambda x: x.replace(year=2013))

df_notimes = pd.DataFrame(columns=['Date', '15', '40', 'year'])
df_notimes['Date'] = df_ordered['Date'].unique()
df_notimes['year'] = df_notimes['Date'].dt.year
list15 = []
list40 = []
for date in df_notimes['Date']:
    list15.append(df_ordered.loc[df_ordered['Date'] == date]['15'].mean())
    list40.append(df_ordered.loc[df_ordered['Date'] == date]['40'].mean())
df_notimes['15'] = list15
df_notimes['40'] = list40
df_notimes['normal_date_timeless'] = df_notimes['Date'].apply(lambda x: x.replace(year=2013))

df_ordered['running15'] = df_ordered['15'].rolling(window=240).mean()
df_notimes['running15'] = df_notimes['15'].rolling(window=10).mean()
df_notimes['running40'] = df_notimes['40'].rolling(window=10).mean()

mean_df = pd.DataFrame(columns=['Date', '15', '40'])
mean_df['Date'] = df_notimes['normal_date_timeless'].unique()
mean_df = mean_df.sort_values(by=['Date'])
mean_df['15'] = df_notimes.groupby('normal_date_timeless')['running15'].mean().values
mean_df['40'] = df_notimes.groupby('normal_date_timeless')['running40'].mean().values
fig, ax = plt.subplots(figsize=(15,10))

# TODO probar a hacer una running average de 10 dias
'''# Agrupar por el año y graficar cada grupo como una línea diferente (valores diarios)
for year, group in df_ordered.groupby('Year'):
    ax.plot(df_ordered.loc[df_ordered['Year'] == year]['normal_date_timeless'], df_ordered.loc[df_ordered['Year'] == year]['running15'], label=year)
'''
#Valores diarios
for year, group in df_notimes.groupby('year'):
    if year >= 2014:
        ax.plot(group['normal_date_timeless'], group['running15'], label=year)
ax.plot(mean_df['Date'], mean_df['15'], color='k', label='Average 2002-2024', linestyle='dotted')
# Añadir etiquetas y título
ax.set_xlabel('Mes')
ax.set_ylabel('Valor')
ax.set_title('Valores por mes para diferentes años a 15m')
ax.legend(title='Año')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
plt.savefig('probes_V5.png')

plt.clf()
fig, ax = plt.subplots(figsize=(15,10))
# Crea un dataframe con la media anual de temperatura
columns = ['Year', 'MeanT']
df_means = pd.DataFrame(columns=columns)
for year, group in df.groupby('Year'):
    dict = {'Year': int(year), 'MeanT': group['15'].mean()}
    df_means = df_means.append(dict, ignore_index=True)
    df_means['Year'] = df_means['Year'].astype(int)
ax.bar(df_means['Year'], df_means['MeanT'])
ax.set_ylim([12, 21])
ax.set_xticks(range(df_means['Year'][0], df_means['Year'][len(df_means['Year'])-1] + 1, 1))
plt.savefig('history.png')
print('hi')