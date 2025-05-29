import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as matplotlib
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
matplotlib.use("TkAgg")

df_mortality = pd.read_excel(r'/home/marcjou/Descargas/OdMClimate Monitoring Mortality_Regions_V2.xlsx', sheet_name='Hoja1')
df_posidonia = pd.read_excel(r'/home/marcjou/Descargas/OdMClimate_FloracióPosidonia_Shook Version.xlsx')
df_visual = pd.read_excel(r'/home/marcjou/Descargas/OdMClimate Visual Census_Shook Version V3.xlsx')
df_medusas = pd.read_excel(r'/home/marcjou/Descargas/Indice de Medusas_Shook Version_V2.xlsx')
colors = {'mortality': {"No impact": "#ccfcb3",  # Green
    "Low impact": "#ffe353",  # Yellow
    "Moderate impact": "#ff8000",  # Light orange
    "Severe impact": "#ff5e59"}, 'posidonia' : {
    "No flowering": "#ccfcb3",  # Green
    "Isolated flowering": "#fff8af",  # Light yellow
    "Small flowering": "#ffe353",  # Yellow
    "Moderate flowering": "#ffb000",  # Light orange
    "Large flowering": "#ff8000",  # Orange
    "Exceptional flowering": "#ff5e59"  # Red
}, 'medusas': {
    "Absence": "#e1dfdf",  # Grey
    "No impact": "#ccfcb3",  # Green
    "Moderate impact": "#ffb000",  # Light orange
    "Severe impact": "#ff5e59"  # Red
}, 'visual': {
    "No impact": "#ccfcb3",  # Green
    "Low impact": "#ffe353",  # Yellow
    "Moderate impact": "#ffb000",  # Light orange
    "Strong impact": "#ff8000",  # Orange
    "Severe impact": "#ff5e59"  # Red
}}
def plot_horizontal_assessment(df, tipus, colors):
    type_counts = df["Type"].value_counts()
    type_percent = type_counts / type_counts.sum() * 100  # Convertir a porcentaje
    color_dict = colors[tipus]
    # Crear la barra horizontal acumulada
    plt.figure(figsize=(8, 2))
    plt.barh([""], [100], color="lightgrey")  # Barra de fondo al 100%
    left = 0
    for t, pct in type_percent.items():
        plt.barh([""], [pct], left=left, color=color_dict[t], label=f"{t} ({pct:.1f}%)")  # Etiqueta con porcentaje
        left += pct

    # Personalización
    plt.xlabel("Percentage")
    plt.title("Accumulated Percentage of 'Type'")
    plt.xlim(0, 100)  # Asegurar que la escala llega al 100%
    plt.legend(title="Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.yticks([])
    plt.tight_layout()  # Ajustar márgenes
    plt.savefig(r'/home/marcjou/Descargas/proba_'+tipus+'.png', bbox_inches="tight")

plot_horizontal_assessment(df_posidonia, 'posidonia', colors)

print('hey')