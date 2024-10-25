import pandas as pd
import numpy as np
import data_manager as dm
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


# Ejemplo de datos
dm = dm.DataManager('hey', 'yo')
df_thresholds = dm.thresholds_df('../src/input_files/Database_T_06_Medes_200207-202409.txt')
depth = df.columns[2:-2].values
thresholds = ['25°C', '26°C', '27°C', '28°C']

values_old_25 = df_thresholds.loc[df_thresholds['year'] < 2024].groupby('depth(m)')['Ndays>=25'].max()
values_old_26 = df_thresholds.loc[df_thresholds['year'] < 2024].groupby('depth(m)')['Ndays>=26'].max()
values_old_27 = df_thresholds.loc[df_thresholds['year'] < 2024].groupby('depth(m)')['Ndays>=27'].max()
values_old_28 = df_thresholds.loc[df_thresholds['year'] < 2024].groupby('depth(m)')['Ndays>=28'].max()

values_25 = df_thresholds.loc[df_thresholds['year'] == 2024].groupby('depth(m)')['Ndays>=25'].max()
values_26 = df_thresholds.loc[df_thresholds['year'] ==2024].groupby('depth(m)')['Ndays>=26'].max()
values_27 = df_thresholds.loc[df_thresholds['year'] == 2024].groupby('depth(m)')['Ndays>=27'].max()
values_28 = df_thresholds.loc[df_thresholds['year'] == 2024].groupby('depth(m)')['Ndays>=28'].max()
# Crear la figura
fig, ax = plt.subplots(figsize=(6, 6))

# Crear las barras apiladas simétricas

ax.barh(depth, values_25, color='#fdcb5c')
ax.barh(depth, values_26, left=values_25, color='#fd8d3c')
ax.barh(depth, values_27, left=values_25 + values_26, color='#e63523')
ax.barh(depth, values_28, left=values_25 + values_26 + values_27, color='#bd0026')

ax.barh(depth, -values_old_25, color='#fdcb5c')
ax.barh(depth, -values_old_26, left=-values_old_25, color='#fd8d3c')
ax.barh(depth, -values_old_27, left=-values_old_25 - values_old_26, color='#e63523')
ax.barh(depth, -values_old_28, left=-values_old_25 - values_old_26 - values_old_27, color='#bd0026')


# Etiquetas y estilo
ax.set_xlabel('Exposure days')
ax.set_ylabel('Depth (m)')
ax.set_title('Exposure days by depth and temperature thresholds')

# Leyenda y límites
ax.legend()
ax.set_xlim(-30, 30)
ax.set_xticks(np.arange(-30, 31, 10))
ax.set_xticklabels([str(abs(x)) for x in np.arange(-30, 31, 10)])
ax.set_yticks(depth)
ax.invert_yaxis()
ax.xaxis.set_ticks_position('top')
ax.axvline(0, color='gray', linewidth=0.8)  # Línea divisoria en el centro

# Mostrar gráfico
plt.tight_layout()

# Personalizar la leyenda
legend_labels = thresholds
legend_colors = ['#fdcb5c', '#fd8d3c', '#e63523', '#bd0026']

# Crear las entradas de la leyenda con colores específicos
legend_handles = [plt.Line2D([0], [0], color=color, lw=2) for color in legend_colors]

# Agregar la leyenda al gráfico
plt.legend(legend_handles, legend_labels, title='Thresholds')
plt.savefig('../chatprueba.png')

print('hi')