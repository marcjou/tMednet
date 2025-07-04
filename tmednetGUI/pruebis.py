import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Crear un DataFrame de ejemplo
np.random.seed(42)
df = pd.DataFrame({
    'x': np.linspace(0, 10, 100),
    'y': np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100)  # Seno con ruido
})

# Calcular la media y desviación estándar de 'y'
media = df['y'].mean()
desviacion = df['y'].std()

# Graficar los datos
plt.plot(df['x'], df['y'], label='Datos', color='blue')

# Línea de la media
plt.axhline(y=media, color='red', linestyle='--', label='Media')

# Banda de variación (media ± desviación estándar)
plt.fill_between(df['x'], media - desviacion, media + desviacion, color='gray', alpha=0.3, label='Variación')

# Etiquetas y leyenda
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.title('Gráfico con Media y Variación usando Pandas')
plt.legend()
plt.grid()

# Mostrar el gráfico
plt.show()
