import os
import numpy as np
import pandas as pd
import seaborn as sns
import individual_sensor as iss

import folium
from matplotlib import pyplot as plt
#directories = os.listdir('Lo que sea')

map_center = [41.9000, 3.2000]

# Crear el mapa usando Folium, centrado en la región y con un zoom adecuado
m = folium.Map(location=map_center, zoom_start=9, tiles='OpenStreetMap')

points = {
            "Cap de Creus Nord (Portaló)": (42.333460, 3.286557 ),
            'Cap de Creus Sud (El Gat)': (42.236976, 3.261413),
            'Medes (Pota del Llop)': (42.049700, 3.225400),
            'Ullastres': (41.8880, 3.2003)
            }

for name, coords in points.items():
    folium.Marker(coords).add_to(m)

m.save('../mapa_sites_catalunya.html')

'''sensor = iss.SensorData('/home/marc/Projects/Mednet/tMednet/src/Centros de Buceo_V1.xlsx', 'site')
sensor.place_coordinates(points)
sensor.plot_temperature_depth()
'''
print('hi')
