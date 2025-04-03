import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as matplotlib
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
import requests

from tqdm import tqdm
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import folium
from folium.plugins import MarkerCluster
from PIL import Image
from cartopy.io.img_tiles import MapTiler
matplotlib.use("TkAgg")

df_mortality = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate Monitoring Mortality_Regions_V2.xlsx', sheet_name='Hoja1')
df_posidonia = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate_FloracióPosidonia_Shook Version.xlsx')
df_visual = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\OdMClimate Visual Census_Shook Version V3.xlsx')
df_medusas = pd.read_excel(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\Indice de Medusas_Shook Version_V2.xlsx')
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

project_colors = {
    'visual' : '#7a1841',
    'medusas' : '#c53985',
    'mortality' : 'ac1520',
    'posidonia': 'cfde35'
}
def plot_horizontal_assessment(df, tipus, colors, region='all'):
    if region!= 'all':
        if region == 'Catalunya':
            df = df.loc[(df['Region'] == 'Costa Brava') | (df['Region'] == 'Tarragona') | (df['Region'] == 'Barcelona')]
        elif region == 'Balear':
            df = df.loc[(df['Region'] == 'Menorca') | (df['Region'] == 'Mallorca') | (df['Region'] == 'Ibiza-Formentera')]
        elif region == 'Murcia':
            df = df.loc[(df['Region'] == 'Murcia')]
        elif region == 'Alboran':
            df = df.loc[(df['Region'] == 'Almería') | (df['Region'] == 'Granada') | (df['Region'] == 'Estrecho')]
    if tipus == 'posidonia':
        col = 'Type'
        type_counts = df[col].value_counts()
        ordered_categories = ["No flowering", "Isolated flowering", "Small flowering", "Moderate flowering", "Large flowering", "Exceptional flowering"]
    elif tipus == 'visual':
        col = 'Tropical. Index'

        num_to_text = {
            0: "No impact",
            1: "Low impact",
            2: "Moderate impact",
            3: "Strong impact",
            4: "Severe impact"
        }
        df[col] = df[col].map(num_to_text)
        type_counts = df[col].value_counts()
        ordered_categories = ["No impact", "Low impact", "Moderate impact", "Strong impact", "Severe impact"]

    elif tipus=='medusas':
        col = 'Condición total'

        num_to_text = {
            0: "Absence",
            1: "No impact",
            2: "Moderate impact",
            3: "Severe impact"
        }
        df[col] = df[col].map(num_to_text)
        type_counts = df[col].value_counts()
        ordered_categories = ["Absence", "No impact", "Moderate impact", "Severe impact"]

    elif tipus == 'mortality':
        col = '% Affected all'
        # Definir los rangos personalizados
        bins = [0, 10, 30, 60, float('inf')]  # Límites de los rangos
        labels = ["No impact", "Low impact", "Moderate impact", "Severe impact"]  # Etiquetas para cada rango

        # Crear una nueva columna con los rangos
        df["Range"] = pd.cut(df[col], bins=bins, labels=labels, right=False)

        # Contar la cantidad de valores en cada rango
        type_counts = df["Range"].value_counts().sort_index()
        ordered_categories = ["No impact", "Low impact", "Moderate impact", "Severe impact"]

    type_counts = type_counts.reindex(ordered_categories)
    type_percent = type_counts / type_counts.sum() * 100
    #type_percent = type_percent.dropna() # Convertir a porcentaje
    color_dict = colors[tipus]
    # Crear la barra horizontal acumulada
    plt.figure(figsize=(8, 2))
    plt.barh([""], [100], color="lightgrey")  # Barra de fondo al 100%
    left = 0
    for t, pct in type_percent.items():
        plt.barh([""], [pct], left=left, color=color_dict[t], label=t)  # f"{t} ({pct:.1f}%)" Etiqueta con porcentaje
        left += pct

    # Personalización
    if tipus == 'visual':
        plt.title("Climate Fish Assessment " + region)
    else:
        plt.title(tipus.capitalize() + " Assessment "+ region)
    plt.xlim(0, 100)
    plt.xticks([0,50,100])
    plt.xlabel('')
    # Asegurar que la escala llega al 100%
    plt.legend(title="Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.yticks([])
    plt.tight_layout()  # Ajustar márgenes
    plt.savefig(r'C:\Users\marcj\Documents\CSIC\OdM\Shook\Barras_'+tipus+ '_' + region +'.png', bbox_inches="tight")


maptiler_url = f"https://api.maptiler.com/maps/basic-v2/256/{{z}}/{{x}}/{{y}}.png?key=acX4BQAXGb3u391t8fks"  # Tu URL de MapTiler
plot_horizontal_assessment(df_mortality, 'mortality', colors, 'Alboran')
plot_horizontal_assessment(df_posidonia, 'posidonia', colors, 'Alboran')
plot_horizontal_assessment(df_medusas, 'medusas', colors, 'Alboran')
plot_horizontal_assessment(df_visual, 'visual', colors, 'Alboran')
print('hey')