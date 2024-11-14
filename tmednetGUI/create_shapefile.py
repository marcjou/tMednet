import geopandas as gpd
import matplotlib.pyplot as plt

# Cargar el shapefile
# Reemplaza 'shapefile_path.shp' con la ruta al archivo de España
mapa_españa = gpd.read_file('/home/marc/Descargas/lineas_limite/SHP_ETRS89/recintos_provinciales_inspire_peninbal_etrs89/recintos_provinciales_inspire_peninbal_etrs89.shp')

# Filtrar solo las provincias de Cataluña
provincias_cataluña = mapa_españa[mapa_españa['NAMEUNIT'].isin(['Barcelona', 'Tarragona', 'Lleida', 'Girona'])]

# Crear el mapa en blanco con los límites de las provincias
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
provincias_cataluña.boundary.plot(ax=ax, color="black")  # Delimitar las provincias en negro
ax.set_title("Mapa de Cataluña con delimitación de provincias")
ax.axis('off')  # Quitar ejes

#plt.show()

provincias_cataluña.to_file("mapa_cataluña_provincias.shp", driver='ESRI Shapefile')