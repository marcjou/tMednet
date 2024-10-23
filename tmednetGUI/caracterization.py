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
fig, ax = plt.subplots(figsize=(15,10))

# TODO no funciona porque esta cogiendo mes como entero. Debo coger la fecha horaria exacta si quiero que me muestre la evolución correcta es decir sumar fecha y hora
# Agrupar por el año y graficar cada grupo como una línea diferente
for year, group in df_ordered.groupby('Year'):
    ax.plot(df_ordered.loc[df_ordered['Year'] == year]['normal_date'], df_ordered.loc[df_ordered['Year'] == year]['15'], label=year)

# Añadir etiquetas y título
ax.set_xlabel('Mes')
ax.set_ylabel('Valor')
ax.set_title('Valores por mes para diferentes años a 15m')
ax.legend(title='Año')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
plt.savefig('probes.png')
# Mostrar la gráfica
plt.show()
print('hi')