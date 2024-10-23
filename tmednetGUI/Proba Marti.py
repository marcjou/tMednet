import os
import numpy as np
import pandas as pd
import seaborn as sns
import individual_sensor as iss
from matplotlib import pyplot as plt
directories = os.listdir('Lo que sea')
points = {
            "Bueco Natura": (36.718302, -3.726206),
            'Boreas': (41.832277, 3.116796),
            'Mar Menuda': (41.721704, 2.939089)
            }

sensor = iss.SensorData('/home/marc/Projects/Mednet/tMednet/src/Centros de Buceo_V1.xlsx', 'multi_center')
sensor.place_coordinates(points)
sensor.plot_temperature_depth()
print('hi')
