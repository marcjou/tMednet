import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

df = pd.read_excel('/home/marc/Documentos/PalazzuPopulationEvolution.xlsx', sheet_name='Conjunt Transectes')
df['Trans+Col'] = df['Transecto'].astype(str) + '_' + df['Id_colony'].astype(str)
dfy = df.copy()
dfy.sort_values('Life_years', ascending=True, inplace=True)
dfy['KM'] = dfy['KM'].fillna('A')
color = {'B': '#d0cece', 'O': '#7f7f7f', 'N': '#000000', 'X': '#5c5c5c', 'A': '#ececec'}
#ax = dfy.plot.barh(x='Trans+Col', y='Mortality_year', width=0.2)
ax = sns.barplot(data=dfy, x='Mortality_year', y='Trans+Col', hue='KM', palette=color, orient='h')
#ax = sns.barplot(data=dfy, y='Mortality_year', x='Trans+Col', hue='KM', palette=color)
for bar in ax.patches:
    bar.set_height(0.5)
ax.set_xlim(int(2003), int(2023))
ax.set_xticks(range(2003, 2024, 1))
ax.get_yaxis().set_visible(False)
plt.show()
print('hi')