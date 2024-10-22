import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202409.txt', sep='\t')
# Recover year and month
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
# Pin point the data for only the JAS months
df_ordered = df.loc[(df['Month'] >= 7) & (df['Month'] <= 9)]

# TODO no funciona porque esta cogiendo mes como entero. Debo coger la fecha horaria exacta si quiero que me muestre la evolución correcta es decir sumar fecha y hora
# Agrupar por el año y graficar cada grupo como una línea diferente
for year, group in df_ordered.groupby('Year'):
    plt.plot(group['Month'], group['15'], label=year)

# Añadir etiquetas y título
plt.xlabel('Mes')
plt.ylabel('Valor')
plt.title('Valores por mes para diferentes años')
plt.legend(title='Año')

# Mostrar la gráfica
plt.show()
print('hi')